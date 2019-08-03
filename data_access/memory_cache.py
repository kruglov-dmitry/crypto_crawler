from constants import CACHE_HOST, CACHE_PORT
from data_access.classes.memory_cache import MemoryCache

LOCAL_CACHE = None


def connect_to_cache(host=CACHE_HOST, port=CACHE_PORT):
    # FIXME NOTE temporary workaround for in-memory caching
    global LOCAL_CACHE
    LOCAL_CACHE = MemoryCache(host, port)
    return LOCAL_CACHE


def get_cache(host=CACHE_HOST, port=CACHE_PORT):
    if LOCAL_CACHE is None:
        return connect_to_cache(host, port)
    return LOCAL_CACHE


def generate_nonce():
    # Additionally, all queries must include a "nonce" POST parameter.
    # The nonce parameter is an integer which must always be greater than the previous nonce used.
    # return int(round(time.time() * 1000))
    cache = get_cache()
    return cache.get_counter()


def get_next_arbitrage_id():
    cache = get_cache()
    return cache.get_arbitrage_id()
