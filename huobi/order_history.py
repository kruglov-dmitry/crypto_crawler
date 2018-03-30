from urllib import urlencode as _urlencode

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file
from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, LOG_ALL_DEBUG, \
    DEBUG_LOG_FILE_NAME, ERROR_LOG_FILE_NAME

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header
from data.Trade import Trade

from huobi.constants import HUOBI_GET_OPEN_ORDERS, HUOBI_DEAL_TIMEOUT, HUOBI_ORDER_HISTORY_LIMIT
from huobi.error_handling import is_error
from enums.status import STATUS


def get_order_history_huobi_post_details(key, pair_name, limit, last_order_id=None):
    final_url = HUOBI_GET_OPEN_ORDERS

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

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get orders history huobi: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_huobi_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """
    orders = []
    if is_error(json_document):

        msg = "get_order_history_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document:
        order = Trade.from_huobi(entry)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders


def get_order_history_huobi(key, pair_name, limit=HUOBI_ORDER_HISTORY_LIMIT, last_order_id=None):

    post_details = get_order_history_huobi_post_details(key, pair_name, limit, last_order_id)

    err_msg = "get_all_orders_huobi for {pair_name}".format(pair_name=pair_name)

    status_code, json_responce = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                             timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_order_history_huobi: {sc} {resp}".format(sc=status_code, resp=json_responce)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    historical_orders = []
    if status_code == STATUS.SUCCESS:
        status_code, historical_orders = get_order_history_huobi_result_processor(json_responce, pair_name)

    return status_code, historical_orders
