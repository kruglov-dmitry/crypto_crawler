from poloniex.constants import POLONIEX_GET_ORDER_HISTORY

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import get_logging_level, LOG_ALL_TRACE

from utils.key_utils import signed_body


def get_order_history_poloniex_post_details(key, currency_name):
    body = {
        'command': 'returnTradeHistory',
        'currencyPair': currency_name,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_ORDER_HISTORY

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_TRACE:
        print res

    return res


def get_orders_history_poloniex(key, currency_name):
    post_details = get_order_history_poloniex_post_details(key, currency_name)

    err_msg = "get poloniex order history"

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=3)

    return error_code, res


def get_order_history_poloniex(key, pair_name, time_start, time_end, limit):
    body = {
        'command': 'returnTradeHistory',
        'currencyPair': pair_name,
        'start': time_start,
        'end': time_end,
        'limit': limit,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_ORDER_HISTORY

    err_msg = "get poloniex order history for time interval"

    post_details = PostRequestDetails(final_url, headers, body)

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=1)

    return error_code, res