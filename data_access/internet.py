import requests
import json
import hmac
import hashlib

from constants import HTTP_TIMEOUT_SECONDS
from enums.status import STATUS

from utils.time_utils import sleep_for
from utils.file_utils import log_to_file
from debug_utils import print_to_console, LOG_ALL_ERRORS, DEBUG_LOG_FILE_NAME, ERROR_LOG_FILE_NAME, \
    LOG_ALL_MARKET_NETWORK_RELATED_CRAP

"""
            NOTE:
            in-efficient blocking implementation better to rely ConnectionPool
"""


def send_request(final_url, error_msg):
    res = STATUS.FAILURE, None
    try:
        responce = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS).json()
        res = STATUS.SUCCESS, responce
        log_to_file(responce, DEBUG_LOG_FILE_NAME)
    except Exception, e:
        res = STATUS.FAILURE, error_msg + str(e)
        msg = "send_request ERROR: {excp} MSG: {e_msg}".format(e_msg=error_msg, excp=str(e))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

    return res


def send_get_request_with_header(final_url, header, error_msg, timeout=HTTP_TIMEOUT_SECONDS):
    res = STATUS.FAILURE, None
    try:
        responce = requests.get(final_url, headers=header, timeout=timeout)
        print responce
        responce = responce.json()
        res = STATUS.SUCCESS, responce
        log_to_file(responce, DEBUG_LOG_FILE_NAME)
    except Exception, e:
        res = STATUS.FAILURE, error_msg + str(e)
        msg = "send_get_request_with_header ERROR: {excp} MSG: {e_msg}".format(e_msg=error_msg, excp=str(e))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

    return res


def send_post_request_with_header(final_url, header, body, error_msg, max_tries, timeout=HTTP_TIMEOUT_SECONDS):
    res = STATUS.FAILURE, None

    try_number = 0
    while try_number < max_tries:
        try_number += 1
        try:
            response = requests.post(final_url, data=body, headers=header, timeout=timeout).json()
            str_repr = json.dumps(response)
            # try to deal with problem - i.e. just wait an retry
            if "EOrder" in str_repr or "Unavailable" in str_repr or "Busy" in str_repr or "ETrade" in str_repr or "EGeneral:Invalid" in str_repr \
                    or "timeout" in str_repr or "Nonce must" in str_repr:
                sleep_for(1)
            else:
                msg = "send_post_request_with_header: YEAH, RESULT: {res} for url={url}".format(res=str_repr, url=final_url)
                log_to_file(msg, DEBUG_LOG_FILE_NAME)
                # NOTE: Consider it as success then, if not - extend possible checks above
                return STATUS.SUCCESS, response

            msg = "send_post_request_with_header: SOME ERROR: RESULT: {res} for url={url}".format(res=response, url=final_url)
            print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
            log_to_file(msg, ERROR_LOG_FILE_NAME)

            res = STATUS.FAILURE, response

        except Exception, e:
            res = STATUS.FAILURE, error_msg + str(e)
            msg = "send_post_request_with_header: Exception: {excp} Msg: {msg} for url={url}".format(excp=error_msg, msg=str(e),
                                                                                         url=final_url)
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, ERROR_LOG_FILE_NAME)
            sleep_for(1)

    return res


def send_delete_request_with_header(final_url, header, body, error_msg, max_tries):
    res = STATUS.FAILURE, None

    try_number = 0
    while try_number < max_tries:
        try_number += 1
        try:
            response = requests.delete(final_url, data=body, headers=header, timeout=HTTP_TIMEOUT_SECONDS).json()
            str_repr = json.dumps(response)
            # try to deal with problem - i.e. just wait an retry
            if "EOrder" in str_repr or "Unavailable" in str_repr or "Busy" in str_repr or "ETrade" in str_repr or "EGeneral:Invalid" in str_repr \
                    or "timeout" in str_repr:
                sleep_for(1)
            else:
                msg = "YEAH, RESULT: {res}".format(res=str_repr)
                log_to_file(msg, DEBUG_LOG_FILE_NAME)
                # NOTE: Consider it as success then, if not - extend possible checks above
                return STATUS.SUCCESS, response

            msg = "SOME ERROR: RESULT: {res}".format(res=response)
            print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
            log_to_file(msg, DEBUG_LOG_FILE_NAME)

            res = STATUS.FAILURE, response

        except Exception, e:
            res = STATUS.FAILURE, error_msg + str(e)
            msg = "send_post_request_with_header: Exception: {excp} Msg: {msg}".format(excp=error_msg, msg=str(e))
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, DEBUG_LOG_FILE_NAME)
            sleep_for(1)

    return res


def send_post_request_signed(final_url, header, body, secret, nonce, error_msg):
    request = requests.Request('POST', final_url, params=body, headers=header)
    signature = hmac.new(secret, request.body, digestmod=hashlib.sha512)
    request.headers['Sign'] = signature.hexdigest()
    request.headers['nonce'] = nonce

    res = None
    with requests.Session() as session:
        res = session.send(request)

    # try:
    #     res = requests.post(final_url, data=json.dumps(body), headers=header, timeout=HTTP_TIMEOUT_SECONDS).json()
    # except Exception, e:
    #     print error_msg, str(e)

    return res
