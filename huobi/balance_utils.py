from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_CHECK_BALANCE, HUOBI_DEAL_TIMEOUT, HUOBI_API_URL, HUOBI_API_ONLY, HUOBI_GET_ACCOUNT_INFO
from huobi.error_handling import is_error
from huobi.account_utils import get_huobi_account

from data.Balance import Balance

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from debug_utils import print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP, ERROR_LOG_FILE_NAME, \
    should_print_debug, get_logging_level, LOG_ALL_DEBUG

from enums.status import STATUS

from utils.key_utils import sign_string_256_base64
from utils.time_utils import get_now_seconds_utc, ts_to_string_utc
from utils.file_utils import log_to_file


def get_balance_huobi_post_details(key):
    path = HUOBI_CHECK_BALANCE + get_huobi_account(key) + "/balance"
    final_url = HUOBI_API_URL + path + "?"

    body = [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=path, msg1=message)

    print msg

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_huobi_result_processor(json_document, timest):
    if not is_error(json_document) and "data" in json_document:
        return STATUS.SUCCESS, Balance.from_huobi(timest, json_document["data"])

    msg = "get_balance_huobi_result_processor - error response - {er}".format(er=json_document)
    log_to_file(msg, ERROR_LOG_FILE_NAME)

    return STATUS.FAILURE, None


def get_balance_huobi(key):

    post_details = get_balance_huobi_post_details(key)

    err_msg = "check huobi balance called"

    timest = get_now_seconds_utc()

    status_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        log_to_file(res, "balance.log")

    if status_code == STATUS.SUCCESS:
        status_code, res = get_balance_huobi_result_processor(res, timest)

    return status_code, res
