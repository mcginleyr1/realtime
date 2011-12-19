import datetime

import tornado.ioloop
import tornado.web
import tornado.websocket

from monetate.config import settings

class SimpleTemplateHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        assert self.template_name, "template_name is missing"

        self.render(self.template_name, ui_port=settings.UI_PORT)


class LandingHandler(SimpleTemplateHandler):
    template_name = 'index.html'


class MetricsHandler(SimpleTemplateHandler):
    template_name = 'metrics.html'


class ChartHandler(tornado.websocket.WebSocketHandler):
    def _send_chart_data_once(self):
        """
        Send the chart data in a message.
        The handler will convert the dict into JSON.

        As of this writing, WebSockets is disabled in FF 8
        and tornado websockets don't work with Chrome 16.
        Safari 5.1.2 works though, woo hoo!
        """

        if not self.stream.closed():
            self.write_message({'foo': 'bar'})

    def _send_chart_data_and_requeue(self):
        if self.stream.closed():
            pass
        else:
            self._send_chart_data_once()

            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(seconds=3),
                self.async_callback(self._send_chart_data_and_requeue)
            )

    def open(self, *args, **kwargs):
        print "WebSocket opened"

    def on_message(self, message):
        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self._send_chart_data_and_requeue)
        )

    def on_close(self):
        print "WebSocket closed"
