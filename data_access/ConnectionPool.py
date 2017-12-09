import gevent.monkey
gevent.monkey.patch_all()
import requests
from gevent.pool import Pool
from constants import POOL_SIZE, CORE_NUM
from utils.time_utils import sleep_for, get_now_seconds_local

from multiprocessing import Pool as MPool


class WorkUnit:
    def __init__(self, url, method, *args):
        self.url = url
        self.method = method
        self.args = args

    def add_future(self, some_future):
        self.future_result = some_future


class ConnectionPool:
    def __init__(self, pool_size=POOL_SIZE, number_of_processes=CORE_NUM):
        self.session = requests.Session()
        self.network_pool = Pool(pool_size)
        self.processing_pool = MPool(processes=number_of_processes)
        self.number_of_processes = number_of_processes

    def async_getS(self, work_units):

        for work_unit in work_units:
            some_future = self.network_pool.spawn(self.session.get, work_unit.url)
            work_unit(self, some_future)
        self.network_pool.join()

        res = []
        for work_unit in work_units:
            res.append(work_unit.method(work_unit.future_result, work_unit.args))

        return res

    def process_async(self, work):

        t0 = get_now_seconds_local()
        results = []

        for exchange_id in work:

            units_per_exchanges = work[exchange_id]

            result = self.processing_pool.apply_async(self.async_getS, (units_per_exchanges, ))
            results.append(result)

        self.processing_pool.close()
        self.processing_pool.join()

        print len(results)

        my_arr = []
        for result in results:
            while not result.ready():
                sleep_for(5)
            my_arr += result.get(timeout=1)

        t2 = get_now_seconds_local()

        print "TOTAL TIME", (t2 - t0)

        return my_arr