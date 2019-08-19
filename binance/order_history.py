from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file
from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, LOG_ALL_DEBUG, \
    DEBUG_LOG_FILE_NAME

from data_access.internet import send_get_request_with_header

from binance.constants import BINANCE_GET_ALL_ORDERS, BINANCE_DEAL_TIMEOUT, BINANCE_ORDER_HISTORY_LIMIT
from binance.rest_api import generate_post_request, get_orders_binance_result_processor
from enums.status import STATUS


def get_order_history_binance_post_details(key, pair_name, limit, last_order_id=None):

    body = {
        "symbol": pair_name,
        "limit": limit,
        "timestamp": get_now_seconds_utc_ms(),
        "recvWindow": 5000
    }

    if last_order_id is not None:
        body["orderId"] = last_order_id

    post_details = generate_post_request(BINANCE_GET_ALL_ORDERS, body, key)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get orders history binance: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_binance(key, pair_name, limit=BINANCE_ORDER_HISTORY_LIMIT, last_order_id=None):

    post_details = get_order_history_binance_post_details(key, pair_name, limit, last_order_id)

    err_msg = "get_all_orders_binance for {pair_name}".format(pair_name=pair_name)

    status_code, json_response = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                              timeout=BINANCE_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_order_history_binance: {sc} {resp}".format(sc=status_code, resp=json_response)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    historical_orders = []
    if status_code == STATUS.SUCCESS:
        msg = "{fn} - error response - {er}".format(fn=get_order_history_binance.func_name, er=json_response)
        status_code, historical_orders = get_orders_binance_result_processor(json_response, pair_name, msg)

    return status_code, historical_orders
