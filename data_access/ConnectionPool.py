import gevent.monkey
gevent.monkey.patch_all()
import requests
from gevent.pool import Pool
from constants import POOL_SIZE, CORE_NUM
from utils.time_utils import sleep_for, get_now_seconds_local
from constants import HTTP_TIMEOUT_SECONDS

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
            some_future = self.network_pool.spawn(self.session.get, work_unit.url, timeout=HTTP_TIMEOUT_SECONDS)
            work_unit.add_future(some_future)
            futures.append(some_future)
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
        return self.async_getS(work)