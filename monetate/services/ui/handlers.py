import datetime
import logging

import tornado.ioloop
import tornado.web
import tornado.websocket

from monetate.config import database, settings
from monetate import keys as redis_keys


class LandingHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class MetricsHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('metrics.html',
                    ui_port=settings.UI_PORT,
                    account_id=kwargs['account_id'],
                    campaign_id=kwargs['campaign_id'])


class MetricDataHandler(tornado.websocket.WebSocketHandler):
    # TODO: Use a separate IOLoop for the WebSocket stuff?

    def _send_metric_data(self, results):
        """
        Send the chart data in a message.
        The handler will convert the dict into JSON.

        As of this writing, WebSockets is disabled in FF 8
        and tornado websockets don't work with Chrome 16.
        Safari 5.1.2 works though, woo hoo!
        """

        if self.stream.closed():
            logging.debug('stream closed, metric data not sent')
        else:
            logging.debug('metric data results: %s' % results)
            #print 'results', results
            # TODO: If both results are None, do not write the message.
            data = {
                'group_control': results[0],
                'group_experiment': results[1],
                'total_sales_control': results[2],
                'total_sales_experiment': results[3],
                'order_value_control': results[4],
                'order_value_experiment': results[5],
            }
            self.write_message(data)


    def _send_metric_data_and_requeue(self, account_id, campaign_id):
        """
        If the WebSocket stream is still open then send the metric data
        and queue this method up again in the event loop.
        """
        if self.stream.closed():
            pass
        else:
            self.redis_client.mget(
                [
                    redis_keys.get_group_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_group_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
                    redis_keys.get_total_sales_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_total_sales_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
                    redis_keys.get_order_value_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_order_value_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
                ],
                self._send_metric_data
            )

            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(seconds=2),
                self.async_callback(self._send_metric_data_and_requeue, account_id, campaign_id)
            )


    def open(self, *args, **kwargs):
        # We could do something fancy here like keep track of all instances of
        # this class at the class level by campaign id and
        # when then when we write the metric data we could iterate over all of
        # the instances and write to all of them at once.
        logging.debug('WebSocket opened, getting redis connection')

        self.redis_client = database.Redis().client


    def on_message(self, message):
        """
        Called on sending of a WebSocket message from the client.
        We don't care what the message is, it's just a signal
        that we can start repeatedly sending the client metric data.
        """
        account_id, campaign_id = message.split('/')
        account_id = int(account_id)
        campaign_id = int(campaign_id)

        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self._send_metric_data_and_requeue, account_id, campaign_id)
        )


    def on_close(self):
        logging.debug('WebSocket closed, closing redis connection')

        self.redis_client.disconnect()
