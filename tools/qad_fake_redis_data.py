import os.path
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monetate import keys
from monetate.config import database

redis_client = database.Redis().client

while True:
    redis_client.incr(keys.get_campaign_key(12345, 'control_group'))
    redis_client.incr(keys.get_campaign_key(12345, 'experiment_group'))
    time.sleep(2)
