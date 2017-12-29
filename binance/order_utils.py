from urllib import urlencode as _urlencode

from data_access.internet import send_get_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from data.Trade import Trade

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from constants import BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_OPEN_ORDERS
from enums.status import STATUS


def get_open_orders_binance_post_details(key, pair_name):
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
        msg = "get_open_orders_binance: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_open_orders_binance(key, pair_name):

    post_details = get_open_orders_binance_post_details(key, pair_name)

    err_msg = "get_orders_binance"

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    print "get_open_orders_binance", res
    orders = []
    if error_code == STATUS.SUCCESS and res is not None:
        orders = get_open_orders_binance_result_processor(res)

    return error_code, orders


def get_open_orders_binance_result_processor(json_document):
    orders = []
    if json_document is not None:
        for entry in json_document:
            order = Trade.from_binance(entry)
            if order is not None:
                orders.append(order)

    return orders
