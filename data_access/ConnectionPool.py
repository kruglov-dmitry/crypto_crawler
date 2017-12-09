import gevent.monkey
gevent.monkey.patch_all()
import requests
from gevent.pool import Pool
from constants import POOL_SIZE, CORE_NUM
from utils.time_utils import sleep_for, get_now_seconds_local

from multiprocessing import Pool as MPool
from utils.file_utils import log_to_file


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

        futures = []
        for work_unit in work_units:
            # with gevent.Timeout(10, False):
            some_future = self.network_pool.spawn(self.session.get, work_unit.url)
            work_unit.add_future(some_future)
            futures.append(some_future)
        #    self.network_pool.join()
        gevent.joinall(futures)

        res = []
        for work_unit in work_units:
            if work_unit.future_result.value.status_code == 200:
                # log_to_file(work_unit.future_result.value.json(), "res.txt")
                res += work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
            else:
                log_to_file(work_unit.url, "error.txt")

        return res

    def process_async(self, work):

        results = self.async_getS(work)

        # for exchange_id in work:

        #     units_per_exchanges = work[exchange_id]

        #     result = self.async_getS(units_per_exchanges)
        #     # result = self.processing_pool.apply_async(self.async_getS, (units_per_exchanges, ))
        #     results += result

        # self.processing_pool.close()
        # self.processing_pool.join()

        # print len(results)

        # my_arr = []
        # for result in results:
        #     while not result.ready():
        #         sleep_for(5)
        #     my_arr += result.get(timeout=1)

        return results

    def process_async_in_process(self, work):
        self.processing_pool.map(self.async_getS, work)
        # batch_size = len(work) / self.number_of_processes

        # chunks = [work[x:x+batch_size] for x in xrange(0, len(work), batch_size)]

        # results = []
        # for x in range(self.number_of_processes):
        #     p.map(mp_worker, data)
        #     # results += self.processing_pool.apply_async(self.async_getS, (chunks[x], ))

        # self.processing_pool.close()
        # self.processing_pool.join()

        # for result in results:
        #     while not result.ready():
        #         sleep(5)
        #     res = result.get(timeout=1)
        #     print res
