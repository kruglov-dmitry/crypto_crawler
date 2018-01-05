import redis as _redis
from utils.exchange_utils import get_exchange_name_by_id
import pickle
import time


class MemoryCache:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def get_counter(self):
        return self.r.incr('nonce')

    def _init_nonce(self):
        ts = int(round(time.time() * 1000))
        self.r.set('nonce', str(ts))

    def update_balance(self, exchange_name, balance):
        self.r.set(exchange_name, pickle.dumps(balance))

    def get_balance(self, exchange_id):
        exchange_name = get_exchange_name_by_id(exchange_id)
        return pickle.loads(self.r.get(exchange_name))