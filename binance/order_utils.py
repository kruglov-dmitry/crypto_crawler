from urllib import urlencode as _urlencode

from binance.constants import BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_OPEN_ORDERS
from binance.error_handling import is_error

from data.Trade import Trade

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from debug_utils import LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, \
    get_logging_level, ERROR_LOG_FILE_NAME

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms


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

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_open_orders_binance_post_details: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_open_orders_binance(key, pair_name):

    post_details = get_open_orders_binance_post_details(key, pair_name)

    err_msg = "get_orders_binance"

    status_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_open_orders_binance: {r}".format(r=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    orders = []
    if status_code == STATUS.SUCCESS:
        status_code, orders = get_open_orders_binance_result_processor(res, pair_name)

    return status_code, orders


def get_open_orders_binance_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """
    orders = []
    if is_error(json_document):

        msg = "get_open_orders_binance_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document:
        order = Trade.from_binance(entry)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders
