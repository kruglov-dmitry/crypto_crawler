import gevent.monkey
gevent.monkey.patch_all()
import requests
from gevent.pool import Pool
from constants import POOL_SIZE
from utils.file_utils import log_to_file


class WorkUnit:
    def __init__(self, url, method, *args):
        self.url = url
        self.method = method
        self.args = args

    def add_future(self, some_future):
        self.future_result = some_future

    def add_post_details(self, post_details):
        self.post_details = post_details


class ConnectionPool:
    def __init__(self, pool_size=POOL_SIZE):
        self.session = requests.Session()
        self.network_pool = Pool(pool_size)

    def async_get_from_list(self, work_units, timeout):

        futures = []
        for work_unit in work_units:
            some_future = self.network_pool.spawn(self.session.get, work_unit.url, timeout=timeout)
            work_unit.add_future(some_future)
            futures.append(some_future)
        gevent.joinall(futures)

        res = []
        for work_unit in work_units:
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == 200:
                res += work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
            else:
                log_to_file(work_unit.url, "error.txt")

        return res

    def async_get_to_list(self, work_units, timeout):

        futures = []
        for work_unit in work_units:
            some_future = self.network_pool.spawn(self.session.get, work_unit.url, timeout=timeout)
            work_unit.add_future(some_future)
            futures.append(some_future)
        gevent.joinall(futures)

        res = []
        for work_unit in work_units:
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == 200:
                res.append(work_unit.method(work_unit.future_result.value.json(), *work_unit.args))
            else:
                log_to_file(work_unit.url, "error.txt")

        return res

    def async_post_to_list(self, work_units, timeout):
        futures = []
        for work_unit in work_units:
            some_future = self.network_pool.spawn(self.session.post,
                                                  work_unit.post_details.final_url,
                                                  data=work_unit.post_details.body,
                                                  headers=work_unit.post_details.header,
                                                  timeout=timeout)
            work_unit.add_future(some_future)
            futures.append(some_future)
        gevent.joinall(futures)

        res = []
        for work_unit in work_units:
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == 200:
                res.append(work_unit.method(work_unit.future_result.value.json(), *work_unit.args))
            else:
                log_to_file(work_unit.url, "error.txt")

        return res

    def process_async(self, work, timeout):
        return self.async_get_from_list(work, timeout)

    def process_async_to_list(self, work, timeout):
        return self.async_get_to_list(work, timeout)

    def process_async_post(self, work, timeout):
        return self.async_post_to_list(work, timeout)
