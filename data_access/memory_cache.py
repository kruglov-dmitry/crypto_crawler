import redis as _redis
from constants import CACHE_HOST, CACHE_PORT


class MemoryCach():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def get_counter(self):
        return self.r.incr('nonce')

    def _init_nonce(self):
        pass

    def get_balance(self, exchange_id):
        return self.r.get(exchange_id)

    def _update_balance(self):
        pass


# FIXME NOTE temporary workaround for in-memory caching

local_cache = MemoryCach(host=CACHE_HOST, port=CACHE_PORT)