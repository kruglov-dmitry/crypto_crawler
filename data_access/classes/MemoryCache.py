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

    def get_arbitrage_id(self):
        return self.r.incr('arbitrage_id')

    def _init_nonce(self):
        ts = int(round(time.time() * 1000))
        self.r.set('nonce', str(ts))

    def update_balance(self, exchange_name, balance):
        self.r.set(exchange_name, pickle.dumps(balance))

    def get_balance(self, exchange_id):
        exchange_name = get_exchange_name_by_id(exchange_id)
        return pickle.loads(self.r.get(exchange_name))

    def get_value(self, key_name):
        return self.r.get(key_name)

    def set_value(self, key_name, key_value):
        return self.r.set(key_name, key_value)

    def cache_order_book(self, order_book):
        """
            We cannot rely on order book time because in case exchange return dublicative order book
            time may be different.

        :param order_book:
        :return:
        """
        key = "{}-{}".format(order_book.exchange_id, order_book.pair_id)
        self.r.set(key, pickle.dumps(order_book))

    def get_last_order_book(self, pair_id, exchange_id):
        key = "{}-{}".format(exchange_id, pair_id)
        value = self.r.get(key)
        if value is None:
            return None

        return pickle.loads(value)
