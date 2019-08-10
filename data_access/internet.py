import gevent.monkey
gevent.monkey.patch_all()

import requests

from constants import HTTP_TIMEOUT_SECONDS, HTTP_SUCCESS
from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.debug_utils import print_to_console, LOG_ALL_ERRORS, DEBUG_LOG_FILE_NAME, ERROR_LOG_FILE_NAME, \
    get_logging_level, LOG_ALL_DEBUG

"""
            NOTE:
            in-efficient blocking implementation better to rely ConnectionPool
"""


def send_request(final_url, error_msg):
    res = STATUS.FAILURE, None

    try:
        response = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS)
        json_response = response.json()

        if get_logging_level() >= LOG_ALL_DEBUG:
            log_to_file(json_response, DEBUG_LOG_FILE_NAME)

        if response.status_code == HTTP_SUCCESS:
            res = STATUS.SUCCESS, json_response
        else:
            res = STATUS.FAILURE, json_response

    except Exception, e:
        log_error_request_failed("send_request", final_url, error_msg, e)

    return res


def send_get_request_with_header(final_url, header, error_msg, timeout=HTTP_TIMEOUT_SECONDS):
    res = STATUS.FAILURE, None
    try:
        response = requests.get(final_url, headers=header, timeout=timeout)
        json_response = response.json()

        if get_logging_level() >= LOG_ALL_DEBUG:
            log_to_file(json_response, DEBUG_LOG_FILE_NAME)

        if response.status_code == HTTP_SUCCESS:
            res = STATUS.SUCCESS, json_response
        else:
            res = STATUS.FAILURE, json_response

    except Exception, e:
        log_error_request_failed("send_get_request_with_header", final_url, error_msg, e)

    return res


def send_post_request_with_header(post_details, error_msg, max_tries, timeout=HTTP_TIMEOUT_SECONDS):
    res = STATUS.FAILURE, None

    try_number = 0
    while try_number < max_tries:
        try_number += 1
        try:
            response = requests.post(post_details.final_url,
                                     data=post_details.body,
                                     headers=post_details.headers,
                                     timeout=timeout)
            json_response = response.json()

            if get_logging_level() >= LOG_ALL_DEBUG:
                msg = "send_post_request_with_header: RESULT: {res} for url={url}".format(
                    res=json_response, url=post_details.final_url)
                log_to_file(msg, DEBUG_LOG_FILE_NAME)

            status = STATUS.SUCCESS if HTTP_SUCCESS == response.status_code else STATUS.FAILURE

            return status, json_response

        except Exception, e:
            log_error_request_failed("send_post_request_with_header", post_details.final_url, error_msg, e)

    return res


def send_delete_request_with_header(post_details, error_msg, max_tries):
    res = STATUS.FAILURE, None

    try_number = 0
    while try_number < max_tries:
        try_number += 1
        try:
            response = requests.delete(post_details.final_url, data=post_details.body, headers=post_details.headers, timeout=HTTP_TIMEOUT_SECONDS)
            json_response = response.json()

            if get_logging_level() >= LOG_ALL_DEBUG:
                msg = "send_delete_request_with_header: RESULT: {res} for url={url}".format(
                    res=json_response, url=post_details.final_url)
                log_to_file(msg, DEBUG_LOG_FILE_NAME)

            status = STATUS.SUCCESS if HTTP_SUCCESS == response.status_code else STATUS.FAILURE

            return status, json_response

        except Exception, e:
            log_error_request_failed("send_delete_request_with_header", post_details.final_url, error_msg, e)

    return res


def log_error_request_failed(func_name, url, error_msg, exception):
    msg = "{func_name}: Exception: {excp} Msg: {msg} for url={url}".format(
        func_name=func_name, excp=exception, msg=error_msg, url=url)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, ERROR_LOG_FILE_NAME)
