import datetime

import tornado.ioloop
import tornado.escape
import tornado.web
import tornado.websocket

from monetate.config import settings
from monetate import keys

GIF = ('GIF89a'
    '\x01\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00\x2c\x00\x00'
    '\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b\x00')

KEYS = ['purchase_total', 'add_to_cart']

class Recorder(tornado.web.RequestHandler):

    def __init__(self, *request, **kwargs):
        super(Recorder,self).__init__(*request,**kwargs)
        self.dispatch_table = {

        }

    def get(self, *args, **kwargs):
        purchase_total = self.get_argument('purchase_total')
        data = tornado.escape.json_decode(qs)
        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self.record, data)
        )
        self.set_header("content-type","image/gif")
        self.write(GIF)
        self.flush()

    def record(self, data):
        """
        Records the data.
        """
        c = brukva.Client()
        c.connect()
        for key in KEYS:
            value = self.get_argument(key, None)
            if key == 'purchase_total':
                update_purchase_total(value)


    def update_purchase_total(self, value):
        brukva.


