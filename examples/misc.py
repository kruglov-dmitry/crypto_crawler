from utils.time_utils import get_now_seconds_utc, get_now_seconds_local
from data_access.memory_cache import generate_nonce


def test_time_epoch():
    t = get_now_seconds_utc()
    t1 = get_now_seconds_local()
    t2 = generate_nonce()
    print "utc", t
    print "local", t1
    print "nonce", t2