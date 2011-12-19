import datetime
import logging

import tornado.ioloop
import tornado.web
import tornado.websocket

from monetate.config import database, settings
from monetate import keys as redis_keys

class SimpleTemplateHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        assert self.template_name, "template_name is missing"

        self.render(self.template_name, ui_port=settings.UI_PORT)


class LandingHandler(SimpleTemplateHandler):
    template_name = 'index.html'


class MetricsHandler(SimpleTemplateHandler):
    template_name = 'metrics.html'


class MetricDataHandler(tornado.websocket.WebSocketHandler):
    # TODO: Use a separate IOLoop for the WebSocket stuff?

    keys = []


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
            print 'results', results
            data = {
                'control_group': results[0],
                'experiment_group': results[1]
            }
            self.write_message(data)


    def _send_metric_data_and_requeue(self, campaign_id):
        """
        If the WebSocket stream is still open then send the metric data
        and queue this method up again in the event loop.
        """
        if self.stream.closed():
            pass
        else:
            self.redis_client.mget(
                [
                    redis_keys.get_campaign_key(campaign_id, 'control_group'),
                    redis_keys.get_campaign_key(campaign_id, 'experiment_group')
                ],
                self._send_metric_data
            )

            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(seconds=3),
                self.async_callback(self._send_metric_data_and_requeue, campaign_id)
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
        campaign_id = int(message)

        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self._send_metric_data_and_requeue, campaign_id)
        )


    def on_close(self):
        logging.debug('WebSocket closed, closing redis connection')

        self.redis_client.disconnect()
