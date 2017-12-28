from urllib import urlencode as _urlencode

from data_access.internet import send_get_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from data.Trade import Trade

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms

from constants import BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_OPEN_ORDERS
from enums.status import STATUS


def get_open_orders_binance_url(key, pair_name):
    final_url = BINANCE_GET_ALL_OPEN_ORDERS

    body = {
        "symbol": pair_name,
        "timestamp": get_now_seconds_utc_ms(),
        "recvWindow": 5000
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    # Yeah, body after that should be empty
    body = {}

    post_details = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(post_details, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return post_details


def get_open_orders_binance(key, pair_name):

    post_details = get_open_orders_binance_url(key, pair_name)

    err_msg = "get_orders_binance"

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    orders = []
    if error_code == STATUS.SUCCESS and res is not None:
        for entry in res:
            order = Trade.from_binance(entry)
            if order is not None:
                orders.append(order)

    return error_code, orders