import redis as _redis
import time
from dao.db import get_arbitrage_id, init_pg_connection


def update_nonce():
    r = _redis.StrictRedis(host='192.168.1.106', port=6379, db=0)
    ts = int(round(time.time() * 1000))
    r.set('nonce', str(ts))


def update_arbitrage_id():
    r = _redis.StrictRedis(host='192.168.1.106', port=6379, db=0)

    pg_conn = init_pg_connection()
    next_arbitrage_id = get_arbitrage_id(pg_conn)
    r.set('arbitrage_id', str(next_arbitrage_id))

update_nonce()
update_arbitrage_id()
