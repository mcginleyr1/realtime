import datetime

import tornado.ioloop
import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html', title='Foo')


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
