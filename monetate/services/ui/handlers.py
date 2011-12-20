import datetime
import logging

import tornado.ioloop
import tornado.web
import tornado.websocket

from monetate.config import database, settings
from monetate import keys as redis_keys


class LandingHandler(tornado.web.RequestHandler):
    def _render_with_campaign_list(self, results):
        self.render('index.html', campaigns=results)

        self.redis_client.disconnect()

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        self.redis_client = database.Redis().client

        self.redis_client.smembers(
            redis_keys.get_account_campaign_list_key(129),
            self._render_with_campaign_list)


class MetricsHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('metrics.html',
                    ui_port=settings.UI_PORT,
                    ui_host=settings.UI_HOST,
                    account_id=kwargs['account_id'],
                    campaign_id=kwargs['campaign_id'])


class RedisWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
        logging.debug('WebSocket opened, getting redis connection')

        self.redis_client = database.Redis().client


    def on_close(self):
        logging.debug('WebSocket closed, closing redis connection')

        self.redis_client.disconnect()


class CampaignMetricDataHandler(RedisWebSocketHandler):
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

            group_control = results[0]
            group_experiment = results[1]
            add_to_cart_count_control = results[6]
            add_to_cart_count_experiment = results[7]

            if group_control and add_to_cart_count_control:
                add_to_cart_control = float(add_to_cart_count_control) / float(group_control)
            else:
                add_to_cart_control = None
            if group_experiment and add_to_cart_count_experiment:
                add_to_cart_experiment = float(add_to_cart_count_experiment) / float(group_experiment)
            else:
                add_to_cart_experiment = None

            data = {
                'group_control': group_control,
                'group_experiment': group_experiment,
                'total_sales_control': results[2],
                'total_sales_experiment': results[3],
                'order_value_control': results[4],
                'order_value_experiment': results[5],
                'add_to_cart_control': add_to_cart_control,
                'add_to_cart_experiment': add_to_cart_experiment,
#                'session_control': results[6],
#                'session_experiment': results[7],
#                'conversion_control': results[8],
#                'conversion_experiment': results[9],
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
                    redis_keys.get_add_to_cart_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_add_to_cart_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
#                    redis_keys.get_session_value_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
#                    redis_keys.get_session_value_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
#                    redis_keys.get_conversion_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
#                    redis_keys.get_conversion_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
                ],
                self._send_metric_data
            )

            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(seconds=2),
                self.async_callback(self._send_metric_data_and_requeue, account_id, campaign_id)
            )


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
