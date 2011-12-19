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
        io = tornado.ioloop.IOLoop.instance()
        account = self.get_argument('act', None)
        group = self.get_argument('grp', None)
        purchase_total = self.get_argument('pch', None)
        cid = self.get_argument('cid', None)
        add_to_cart = self.get_argument('atc', None)
        new_customer = self.get_argument('nc', None)
        if cid:
            io.add_callback(self.async_callback(self.purchase_total_update, account, cid, group, purchase_total))
            io.add_callback(self.async_callback(self.add_to_cart_update, account, cid, group, add_to_cart))
            io.add_callback(self.async_callback(self.add_to_total_sales, account, cid, group, purchase_total))
            io.add_callback(self.async_callback(self.add_to_group, account, cid, group))
            io.add_callback(self.async_callback(self.update_conversion, account, cid, group, purchase_total))
            io.add_callback(self.async_callback(self.update_session_value, account, cid, group, purchase_total))
        io.add_callback(self.async_callback(self.add_to_new_visitors, account, new_customer))
        self.set_header("content-type","image/gif")
        self.write(GIF)
        self.flush()


    def purchase_total_update(self, account, cid, group, value):
        if value:
            key = keys.get_order_value_key(account, cid, group)
            self.redis.hincrby(key, 'value', int(float(value)))
            self.redis.hincrby(key, 'count', 1)

    def add_to_cart_update(self, account, cid, group, value):
        if value:
            key = keys.get_add_to_cart_key(account, cid, group)
            self.redis.incr(key)

    def add_to_total_sales(self, account, cid, group, value):
        if value:
            key = keys.get_total_sales_key(account, cid, group)
            self.redis.incrby(key, int(float(value)))

    def add_to_group(self, account, cid, group):
        key = keys.get_group_key(account,cid, group)
        self.redis.incr(key)

    def update_conversion(self, account, cid, group, value):
        key = keys.get_conversion_key(account, cid, group)
        if value:
            self.redis.hincrby(key, 'value', 1)
        self.redis.hincrby(key, 'count', 1)

    def add_to_new_visitors(self, account, value):
        if value:
            key = keys.get_new_visitors_key(account)
            self.redis.incr(key)

    def update_session_value(self, account, cid, group, value):
        key = keys.get_session_value_key(account, cid, group)
        if value:
            self.redis.hincrby(key, 'value', int(float(value)))
        self.redis.hincrby(key, 'count', 1)


