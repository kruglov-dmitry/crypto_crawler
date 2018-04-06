import redis as _redis
import time
from dao.db import get_arbitrage_id, init_pg_connection


def update_nonce():
    r = _redis.StrictRedis(host='54.193.19.230', port=6379, db=0)
    ts = int(round(time.time() * 1000))
    r.set('nonce', str(ts))


def update_arbitrage_id():
    r = _redis.StrictRedis(host='54.193.19.230', port=6379, db=0)

    pg_conn = init_pg_connection(_db_host="pg.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")
    next_arbitrage_id = get_arbitrage_id(pg_conn)
    r.set('arbitrage_id', str(next_arbitrage_id))

# update_nonce()
# update_arbitrage_id()a


def show_failed_orders():
    from data_access.message_queue import QUEUE_TOPICS, ORDERS_MSG, FAILED_ORDERS_MSG
    r = _redis.StrictRedis(host='54.193.19.230', port=6379, db=0)

    for topic_id in QUEUE_TOPICS:
        print "For {nn} topic we have {ll} messages".format(nn=topic_id, ll=r.llen(topic_id))

    print "For {nn} topic we have {ll} messages".format(nn=FAILED_ORDERS_MSG, ll=r.llen(topic_id))
    print "For {nn} topic we have {ll} messages".format(nn=ORDERS_MSG, ll=r.zcard(topic_id))


show_failed_orders()
