import time
import redis as _redis

from dao.db import get_arbitrage_id, init_pg_connection
from data_access.message_queue import QUEUE_TOPICS

# FIXME NOTE:
# 1. Read settings from cfg file
# 2. Add utility to get statistics from various queue
# 3. Add quick check that redis & OPTIONALLY AFTER WE MOVE pg BACK accessible

DEFAULT_REDIS_HOST = '54.193.19.230'

def update_nonce(host=DEFAULT_REDIS_HOST):
    r = _redis.StrictRedis(host=host, port=6379, db=0)
    ts = int(round(time.time() * 1000))
    r.set('nonce', str(ts))


def update_arbitrage_id(host=DEFAULT_REDIS_HOST):
    r = _redis.StrictRedis(host=host, port=6379, db=0)

    pg_conn = init_pg_connection(_db_host="192.168.1.106",
                                 _db_port=5432, _db_name="crypto")
    next_arbitrage_id = get_arbitrage_id(pg_conn)
    r.set('arbitrage_id', str(next_arbitrage_id))


def show_failed_orders(host=DEFAULT_REDIS_HOST):
    r = _redis.StrictRedis(host=host, port=6379, db=0)

    for topic_id in QUEUE_TOPICS:
        print "For {nn} topic we have {ll} messages".format(nn=topic_id, ll=r.llen(topic_id))


show_failed_orders()
