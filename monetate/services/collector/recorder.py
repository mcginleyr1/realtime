import datetime

import tornado.ioloop
import tornado.escape
import tornado.web
import tornado.websocket

from monetate.config import settings

GIF = ('GIF89a'
    '\x01\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00\x2c\x00\x00'
    '\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b\x00')

class Recorder(tornado.web.RequestHandler):

    def __init__(self, *request, **kwargs):
        super(Recorder,self).__init__(*request,**kwargs)
        self.dispatch_table = {

        }

    def get(self, *args, **kwargs):
        qs = self.get_argument('encoded')
        data = escape.json_decode(qs)
        tornado.ioloop.IOLoop.instance().add_callback(self.record, data)
        #tornado.ioloop.IOLoop.instance().add_callback(
        #    self.async_callback(self._send_chart_data_and_requeue)
        #)
        self.set_header("content-type","image/gif")
        self.write(GIF)
        self.flush()

    def record(self, data):
        """
        Records the data.
        """
        for key, value in data.iteritems():
            print key, value
