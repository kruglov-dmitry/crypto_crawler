from urllib import urlencode as _urlencode

from data_access.internet import send_get_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from data.Balance import Balance

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc, get_now_seconds_utc_ms

from constants import BINANCE_CHECK_BALANCE, BINANCE_DEAL_TIMEOUT
from enums.status import STATUS


def get_balance_binance_post_details(key):
    final_url = BINANCE_CHECK_BALANCE

    body = {
        "timestamp": get_now_seconds_utc_ms(),
        "recvWindow": 5000
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_binance_result_processor(json_document, timest):
    if json_document is not None and "balances" in json_document:
        return Balance.from_binance(timest, json_document)

    return None


def get_balance_binance(key):
    """

    """

    post_details = get_balance_binance_post_details(key)

    err_msg = "check binance balance called"

    timest = get_now_seconds_utc()

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    if error_code == STATUS.SUCCESS and res is not None and "balances" in res:
        res = Balance.from_binance(timest, res)

    return error_code, res