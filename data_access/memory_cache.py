import redis as _redis
from constants import CACHE_HOST, CACHE_PORT
from utils.exchange_utils import get_exchange_name_by_id
import pickle


local_cache = None


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
        pass

    def update_balance(self, exchange_name, balance):
        self.r.set(exchange_name, pickle.dumps(balance))

    def get_balance(self, exchange_id):
        exchange_name = get_exchange_name_by_id(exchange_id)
        return pickle.loads(self.r.get(exchange_name))


def connect_to_cache():
    # FIXME NOTE temporary workaround for in-memory caching
    global local_cache
    local_cache = MemoryCache(host=CACHE_HOST, port=CACHE_PORT)
    return local_cache


def get_cache():
    global local_cache
    if local_cache is None:
        return connect_to_cache()
    return local_cache


def generate_nonce():
    # Additionally, all queries must include a "nonce" POST parameter.
    # The nonce parameter is an integer which must always be greater than the previous nonce used.
    # FIXME - store in db
    # return int(round(time.time() * 1000))
    global local_cache
    return local_cache.get_counter()
