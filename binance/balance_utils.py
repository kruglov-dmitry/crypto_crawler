from binance.constants import BINANCE_CHECK_BALANCE, BINANCE_DEAL_TIMEOUT
from binance.error_handling import is_error
from binance.rest_api import generate_post_request

from data.balance import Balance

from data_access.internet import send_get_request_with_header

from debug_utils import print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP, ERROR_LOG_FILE_NAME, \
    should_print_debug, get_logging_level, LOG_ALL_DEBUG

from enums.status import STATUS

from utils.time_utils import get_now_seconds_utc, get_now_seconds_utc_ms
from utils.file_utils import log_to_file


def get_balance_binance_post_details(key):
    final_url = BINANCE_CHECK_BALANCE

    body = {
        "timestamp": get_now_seconds_utc_ms(),
        "recvWindow": 5000
    }

    res = generate_post_request(final_url, body, key)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_binance_result_processor(json_document, timest):
    if not is_error(json_document) and "balances" in json_document:
        return STATUS.SUCCESS, Balance.from_binance(timest, json_document)

    msg = "get_balance_binance_result_processor - error response - {er}".format(er=json_document)
    log_to_file(msg, ERROR_LOG_FILE_NAME)

    return STATUS.FAILURE, None


def get_balance_binance(key):

    post_details = get_balance_binance_post_details(key)

    err_msg = "check binance balance called"

    timest = get_now_seconds_utc()

    status_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                    timeout=BINANCE_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        log_to_file(res, "balance.log")

    if status_code == STATUS.SUCCESS:
        status_code, res = get_balance_binance_result_processor(res, timest)

    return status_code, res
