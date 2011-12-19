import os.path
import random
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monetate import keys
from monetate.config import database

redis_client = database.Redis().client

ACCOUNT_ID = 52
CAMPAIGN_ID = 12345

order_value_key_control = keys.get_order_value_key(ACCOUNT_ID, CAMPAIGN_ID, keys.GROUP_CONTROL)
order_value_key_experiment = keys.get_order_value_key(ACCOUNT_ID, CAMPAIGN_ID, keys.GROUP_EXPERIMENT)

redis_client.incrby(order_value_key_control, 142)
redis_client.incrby(order_value_key_experiment, 148)

while True:
    redis_client.incr(keys.get_group_key(ACCOUNT_ID, CAMPAIGN_ID, keys.GROUP_CONTROL))
    redis_client.incr(keys.get_total_sales_key(ACCOUNT_ID, CAMPAIGN_ID, keys.GROUP_CONTROL))

    if random.randint(0, 1) == 1:
        redis_client.incr(keys.get_group_key(ACCOUNT_ID, CAMPAIGN_ID, keys.GROUP_EXPERIMENT))
        redis_client.incr(keys.get_total_sales_key(ACCOUNT_ID, CAMPAIGN_ID, keys.GROUP_EXPERIMENT))

    if random.randint(0, 1) == 1:
        amount = random.randint(-1, 1)
        redis_client.incrby(order_value_key_control, amount)
    if random.randint(0, 1) == 1:
        redis_client.incrby(order_value_key_experiment, random.randint(-1, 1))

    time.sleep(0.1)
