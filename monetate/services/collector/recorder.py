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

Redis = Redis()
redis = Redis.client

class Recorder(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        io = tornado.ioloop.IOLoop.instance()
        account = self.get_argument('act', None)
        group = self.get_argument('grp', 0)
        purchase_total = self.get_argument('pch', None)
        cid = self.get_argument('cid', None)
        add_to_cart = self.get_argument('atc', None)
        new_customer = self.get_argument('nc', None)
        if group == 0:
            io.add_callback(self.async_callback(self.purchase_total_control_update, account, purchase_total))
        if cid:
            io.add_callback(self.async_callback(self.update_account_list, account))
            io.add_callback(self.async_callback(self.update_account_campaign_list, account, cid))
            io.add_callback(self.async_callback(self.purchase_total_update, account, cid, group, purchase_total))
            io.add_callback(self.async_callback(self.add_to_cart_update, account, cid, group, add_to_cart))
            io.add_callback(self.async_callback(self.add_to_total_sales, account, cid, group, purchase_total))
            io.add_callback(self.async_callback(self.add_to_group, account, cid, group))
            io.add_callback(self.async_callback(self.update_conversion, account, cid, group, purchase_total))
            io.add_callback(self.async_callback(self.update_session_value, account, cid, group, purchase_total))
        io.add_callback(self.async_callback(self.add_to_new_visitors, account, new_customer))
        self.set_default_headers()
        self.set_header("Content-Type","image/gif")
        self.write(GIF)
        self.flush()


    def purchase_total_update(self, account, cid, group, value):
        if value:
            key = keys.get_order_value_key(account, cid, group)
            redis.hincrby(key, 'value', float(value))
            redis.hincrby(key, 'count', 1)

    def purchase_total_control_update(self, account, value):
        if value:
            key = keys.get_control_purchase_total_key(account)
            redis.hincrby(key, 'value', float(value))
            redis.hincrby(key, 'count', 1)

    def add_to_cart_update(self, account, cid, group, value):
        if value:
            key = keys.get_add_to_cart_key(account, cid, group)
            redis.incr(key)

    def add_to_total_sales(self, account, cid, group, value):
        if value:
            key = keys.get_total_sales_key(account, cid, group)
            redis.incrby(key, float(value))

    def add_to_group(self, account, cid, group):
        key = keys.get_group_key(account,cid, group)
        redis.incr(key)

    def update_conversion(self, account, cid, group, value):
        key = keys.get_conversion_key(account, cid, group)
        if value:
            redis.hincrby(key, 'value', 1)
        redis.hincrby(key, 'count', 1)

    def add_to_new_visitors(self, account, value):
        if value:
            key = keys.get_new_visitors_key(account)
            redis.incr(key)

    def update_session_value(self, account, cid, group, value):
        key = keys.get_session_value_key(account, cid, group)
        if value:
            redis.hincrby(key, 'value', float(value))
        redis.hincrby(key, 'count', 1)

    def update_account_list(self, account):
        key = keys.get_account_list_key()
        redis.sadd(key, account)

    def update_account_campaign_list(self, account, cid):
        key = keys.get_account_campaign_list_key(account)
        redis.sadd(key, cid)