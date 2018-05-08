import gevent.monkey
gevent.monkey.patch_all()
import requests
from gevent.pool import Pool

from constants import POOL_SIZE, HTTP_SUCCESS

from utils.file_utils import log_to_file
from debug_utils import get_logging_level, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME, POST_RESPONCE_FILE_NAME

from enums.http_request import HTTP_REQUEST
from enums.status import STATUS


def log_responce_cant_be_parsed(work_unit, file_name=None):

    json_responce = ""
    try:
        json_responce = work_unit.future_result.value.json()
    except:
        pass

    msg = """   ERROR
    For url {url} Response {resp} can't be parsed.
    HTTP Responce code: {hc}
    JSON Data if any: {js} 
    """.format(url=work_unit.url, resp=work_unit.future_result.value, hc=work_unit.future_result.value.status_code,
               js=json_responce)
    log_to_file(msg, ERROR_LOG_FILE_NAME)

    if file_name is not None:
        log_to_file(msg, file_name)

    return msg


def log_responce(work_unit):
    json_responce = ""
    try:
        json_responce = work_unit.future_result.value.json()
    except:
        pass

    if len(json_responce) > 0:
        msg = "For url {url} response {resp}".format(url=work_unit.url, resp=json_responce)
    else:
        msg = "For url {url} response {status_code}".format(url=work_unit.url, status_code=work_unit.future_result.value)

    log_to_file(msg, POST_RESPONCE_FILE_NAME)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class ConnectionPool:
    def __init__(self, pool_size=POOL_SIZE):
        self.session = requests.Session()
        self.pool_size = pool_size
        self.network_pool = Pool(self.pool_size)

    def _process_futures(self, work_units_batch):
        """
            Operate under `WorkUnit` objects after returning from async calls.
            Try to apply job specific constructor method for responce returned by exchange.
            In case constructor method fail for any reason - try to wrap all available details into debug string.

        :param work_units_batch:
        :return: array of either object, parsed from exchange responce or error messages as string
        """
        res = []
        for work_unit in work_units_batch:
            if get_logging_level() >= LOG_ALL_DEBUG:
                log_responce(work_unit)

            result = None

            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == HTTP_SUCCESS:
                try:
                    result = work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
                except:
                    pass

                if result is not None:
                    if type(result) is list:
                        res += result
                    else:
                        res.append(result)
                else:
                    result = log_responce_cant_be_parsed(work_unit)
                    res.append(result)
            else:
                result = log_responce_cant_be_parsed(work_unit)
                res.append(result)

        return res

    def async_get_to_list(self, work_units, timeout):

        res = []

        for work_units_batch in batch(work_units, self.pool_size):
            futures = []
            for work_unit in work_units_batch:
                some_future = self.network_pool.spawn(self.session.get, work_unit.url, timeout=timeout)
                work_unit.add_future(some_future)
                futures.append(some_future)
            gevent.joinall(futures)

            res += self._process_futures(work_units_batch)

        return res

    def async_post_to_list(self, work_units, timeout):
        res = []

        for work_units_batch in batch(work_units, self.pool_size):
            futures = []
            for work_unit in work_units_batch:
                some_future = self.network_pool.spawn(self.session.post,
                                                      work_unit.post_details.final_url,
                                                      data=work_unit.post_details.body,
                                                      headers=work_unit.post_details.headers,
                                                      timeout=timeout)
                work_unit.add_future(some_future)
                futures.append(some_future)
            gevent.joinall(futures)

            res += self._process_futures(work_units_batch)

        return res

    def process_async_to_list(self, work, timeout):
        return self.async_get_to_list(work, timeout)

    def process_async_post(self, work, timeout):
        return self.async_post_to_list(work, timeout)

    def _get_http_method_by_type(self, http_method_type):
        return {
            HTTP_REQUEST.POST: self.session.post,
            HTTP_REQUEST.GET: self.session.get
        }[http_method_type]

    def process_async_custom(self, work_units, timeout):
        """
        :param work_units:
        :param timeout:
        :return:    error_code, failure in case at least one of query were problematic in processing
                    list of results, for failed query must be set to None
        """

        err_code = STATUS.SUCCESS

        futures = []
        for work_unit in work_units:
            http_method = self._get_http_method_by_type(work_unit.http_method)
            some_future = self.network_pool.spawn(http_method,
                                                  work_unit.post_details.final_url,
                                                  data=work_unit.post_details.body,
                                                  headers=work_unit.post_details.headers,
                                                  timeout=timeout)
            work_unit.add_future(some_future)
            futures.append(some_future)
        gevent.joinall(futures)

        res = []
        res += self._process_futures(work_units)

        return err_code, res
