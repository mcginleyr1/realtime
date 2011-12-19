import decimal

import tornado.ioloop
import tornado.escape
import tornado.web
import tornado.websocket

from monetate.config import settings
from monetate import keys
from monetate.config.database import Redis

GIF = ('GIF89a'
    '\x01\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00\x2c\x00\x00'
    '\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b\x00')

KEYS = ['purchase_total', 'add_to_cart']

class Recorder(tornado.web.RequestHandler):

    def __init__(self, *request, **kwargs):
        redis = Redis()
        self.redis = redis.client
        super(Recorder,self).__init__(*request,**kwargs)
        self.dispatch_table = {

        }

    def get(self, *args, **kwargs):
        account = self.get_argument('act')
        group = self.get_argument('grp')
        purchase_total = self.get_argument('pt', None)
        if purchase_total:
            tornado.ioloop.IOLoop.instance().add_callback(
                self.async_callback(self.request_purchase_total_update, account, group, purchase_total)
            )
        self.set_header("content-type","image/gif")
        self.write(GIF)
        self.flush()


    def request_purchase_total_update(self, account, group, value):
        key = keys.get_order_value_key(account, group)
        self.redis.hincrby(key, 'value', float(value))
        self.redis.hincrby(key, 'count', 1)



