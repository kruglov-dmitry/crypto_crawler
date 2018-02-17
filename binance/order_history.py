from urllib import urlencode as _urlencode

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file
from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header
from data.Trade import Trade

from binance.constants import BINANCE_GET_ALL_ORDERS, BINANCE_DEAL_TIMEOUT, BINANCE_ORDER_HISTORY_LIMIT
from enums.status import STATUS


def get_order_history_binance_post_details(key, pair_name, limit, last_order_id=None):
    final_url = BINANCE_GET_ALL_ORDERS

    if last_order_id is not None:
        body = {
            "symbol": pair_name,
            "limit": limit,
            "orderId": last_order_id,
            "timestamp": get_now_seconds_utc_ms(),
            "recvWindow": 5000
        }
    else:
        body = {
            "symbol": pair_name,
            "limit": limit,
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
        msg = "get orders history binance: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_binance_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """
    orders = []
    if json_document is None:
        return orders

    for entry in json_document:
        order = Trade.from_binance(entry)
        if order is not None:
            orders.append(order)

    return orders


def get_order_history_binance(key, pair_name, limit=BINANCE_ORDER_HISTORY_LIMIT, last_order_id=None):

    post_details = get_order_history_binance_post_details(key, pair_name, limit, last_order_id)

    err_msg = "get_all_orders_binance for {pair_name}".format(pair_name=pair_name)

    error_code, json_responce = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                             timeout=BINANCE_DEAL_TIMEOUT)

    print error_code, json_responce
    # HTTP Responce code 200, {u'msg': u"Timestamp for this request was 1000ms ahead of the server's time.", u'code': -1021}
    if 'code' in json_responce:
        error_code = STATUS.FAILURE

    historical_orders = []
    if error_code == STATUS.SUCCESS:
        historical_orders = get_order_history_binance_result_processor(json_responce, pair_name)

    return error_code, historical_orders
