from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_CHECK_BALANCE, HUOBI_DEAL_TIMEOUT
from huobi.error_handling import is_error
from huobi.market_utils import get_huobi_account

from data.Balance import Balance

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from debug_utils import print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP, ERROR_LOG_FILE_NAME, \
    should_print_debug, get_logging_level, LOG_ALL_DEBUG

from enums.status import STATUS

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc, get_now_seconds_utc_ms
from utils.file_utils import log_to_file


def get_balance_huobi_post_details(key):
    final_url = HUOBI_CHECK_BALANCE + get_huobi_account() + "/balance"

    body = {}

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_huobi_result_processor(json_document, timest):
    if not is_error(json_document):
        return STATUS.SUCCESS, Balance.from_huobi(timest, json_document)

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
