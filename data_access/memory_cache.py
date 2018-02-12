from constants import CACHE_HOST, CACHE_PORT
from data_access.classes.MemoryCache import MemoryCache

local_cache = None


def connect_to_cache(host=CACHE_HOST, port=CACHE_PORT):
    # FIXME NOTE temporary workaround for in-memory caching
    global local_cache
    local_cache = MemoryCache(host, port)
    return local_cache


def get_cache(host=CACHE_HOST, port=CACHE_PORT):
    global local_cache
    if local_cache is None:
        return connect_to_cache(host, port)
    return local_cache


def generate_nonce():
    # Additionally, all queries must include a "nonce" POST parameter.
    # The nonce parameter is an integer which must always be greater than the previous nonce used.
    # return int(round(time.time() * 1000))
    cache = get_cache()
    return cache.get_counter()


def get_next_arbitrage_id():
    cache = get_cache()
    return cache.get_arbitrage_id()
