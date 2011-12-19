import datetime

import tornado.ioloop
import tornado.web
import tornado.websocket

from monetate.config import settings

class Recorder(tornado.web.RequestHandler):
    def __init__(self):
        self.add_handler(fd, self.parse, self.WRITE)

    def get(self, *args, **kwargs):
        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self._send_chart_data_and_requeue)
        )
        self.write(settings.PIXEL)
        self.flush()


    def parse(self, qs):
        """
        Parse the query string data into format that makes it easy for us to record from.
        """

    def record(self, data):
        """
        Records the data.
        """