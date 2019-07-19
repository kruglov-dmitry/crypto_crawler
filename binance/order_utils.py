from binance.constants import BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_OPEN_ORDERS
from binance.rest_api import generate_post_request, get_orders_binance_result_processor

from data_access.internet import send_get_request_with_header

from debug_utils import LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, \
    get_logging_level

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc_ms


def get_open_orders_binance_post_details(key, pair_name):

    body = {
        "symbol": pair_name,
        "timestamp": get_now_seconds_utc_ms(),
        "recvWindow": 5000
    }

    post_details = generate_post_request(BINANCE_GET_ALL_OPEN_ORDERS, body, key)

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
    msg = "get_open_orders_binance_result_processor - error response - {er}".format(er=json_document)

    return get_orders_binance_result_processor(json_document, pair_name, msg)
