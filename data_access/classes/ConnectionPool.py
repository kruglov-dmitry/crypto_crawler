import gevent.monkey
gevent.monkey.patch_all()
import requests
from gevent.pool import Pool

from constants import POOL_SIZE, HTTP_SUCCESS

from utils.file_utils import log_to_file
from debug_utils import get_logging_level, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME, POST_RESPONCE_FILE_NAME

from enums.http_request import HTTP_REQUEST
from enums.status import STATUS


def log_responce_cant_be_parsed(work_unit, file_name):
    msg = "For url {url} response {resp} can't be parsed. Next line should be json if any. ".format(
        url=work_unit.url, resp=work_unit.future_result.value)
    log_to_file(msg, ERROR_LOG_FILE_NAME)
    log_to_file(msg, file_name)

    json_responce = ""
    try:
        json_responce = work_unit.future_result.value.json()
        log_to_file(json_responce, ERROR_LOG_FILE_NAME)
        log_to_file(json_responce, file_name)
    except:
        pass

    if work_unit.future_result.value is not None:
        msg = "ERROR: returned code - {err} Json: {js}".format(err=work_unit.future_result.value.status_code, js=json_responce)
    else:
        msg = "ERROR: returned code - None Json: {js}".format(js=json_responce)

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
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == HTTP_SUCCESS:
                if get_logging_level() >= LOG_ALL_DEBUG:
                    log_responce(work_unit)
                res += work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
            else:
                log_to_file(work_unit.url, ERROR_LOG_FILE_NAME)

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
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == HTTP_SUCCESS:
                if get_logging_level() >= LOG_ALL_DEBUG:
                    log_responce(work_unit)
                some_ticker = work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
                if some_ticker is not None:
                    res.append(some_ticker)
                else:
                    res.append(None)
                    log_responce_cant_be_parsed(work_unit, "bad_tickers.txt")
            else:
                res.append(None)
                log_responce_cant_be_parsed(work_unit, POST_RESPONCE_FILE_NAME)

        return res

    def async_post_to_list(self, work_units, timeout):
        futures = []
        for work_unit in work_units:
            some_future = self.network_pool.spawn(self.session.post,
                                                  work_unit.post_details.final_url,
                                                  data=work_unit.post_details.body,
                                                  headers=work_unit.post_details.headers,
                                                  timeout=timeout)
            work_unit.add_future(some_future)
            futures.append(some_future)
        gevent.joinall(futures)

        res = []
        for work_unit in work_units:
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == HTTP_SUCCESS:
                if get_logging_level() >= LOG_ALL_DEBUG:
                    log_responce(work_unit)
                some_result = work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
                # FIXME NOTE performance
                if type(some_result) is list:
                    res += some_result
                else:
                    res.append(some_result)
            else:
                err_msg = log_responce_cant_be_parsed(work_unit, POST_RESPONCE_FILE_NAME)

                some_result = work_unit.method(err_msg, *work_unit.args)
                res.append(some_result)

        return res

    def process_async(self, work, timeout):
        return self.async_get_from_list(work, timeout)

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
        for work_unit in work_units:
            if work_unit.future_result.value is not None and work_unit.future_result.value.status_code == HTTP_SUCCESS:
                if get_logging_level() >= LOG_ALL_DEBUG:
                    log_responce(work_unit)
                some_result = work_unit.method(work_unit.future_result.value.json(), *work_unit.args)
                # FIXME NOTE performance
                if type(some_result) is list:
                    res += some_result
                else:
                    res.append(some_result)
            else:
                err_code = STATUS.FAILURE
                res.append(None)
                log_responce_cant_be_parsed(work_unit, POST_RESPONCE_FILE_NAME)

        return err_code, res
