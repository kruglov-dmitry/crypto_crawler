import gevent

from data_access.classes.connection_pool import ConnectionPool
from utils.time_utils import sleep_for


def test_pool():

    def heavy_load():
        sleep_for(3)
        print "heavy_load"

    def more_heavy_load():
        sleep_for(30)
        print "more_heavy_load"

    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]
    processor = ConnectionPool(10)

    iters = []
    for x in xrange(100):
        iters.append(x)

    for work_batch in batch(iters, 10):
        futures = []
        for x in work_batch:
            futures.append(processor.network_pool.spawn(more_heavy_load))
        gevent.joinall(futures)

    for work_batch in batch(iters, 10):
        futures = []
        for x in work_batch:
            futures.append(processor.network_pool.spawn(heavy_load))
        gevent.joinall(futures)
