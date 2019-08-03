from poloniex.constants import POLONIEX_GET_ORDER_HISTORY, POLONIEX_NUM_OF_DEAL_RETRY, POLONIEX_ORDER_HISTORY_LIMIT
from poloniex.error_handling import is_error

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from data.trade import Trade

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file
from utils.key_utils import signed_body
from utils.time_utils import get_now_seconds_utc

from enums.status import STATUS


def get_order_history_poloniex_post_details(key, pair_name, time_start, time_end, limit):
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

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get orders history poloniex: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def parse_orders_currency(json_document, pair_name):

    orders = []

    for entry in json_document:
        trade = Trade.from_poloniex_history(entry, pair_name)
        if trade is not None:
            orders.append(trade)

    return orders


def get_order_history_poloniex_result_processor(json_document, pair_name):
    """
        json_document - response from exchange api as json string
        pair_name - for backwords compabilities
    """
    orders = []
    if is_error(json_document):

        msg = "get_order_history_poloniex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    if pair_name != "all":
        orders = parse_orders_currency(json_document, pair_name)
    else:
        for pair_name in json_document:
            orders += parse_orders_currency(json_document[pair_name], pair_name)

    return STATUS.SUCCESS, orders


def get_order_history_poloniex(key, pair_name, time_start=0, time_end=get_now_seconds_utc(), limit=POLONIEX_ORDER_HISTORY_LIMIT):
    post_details = get_order_history_poloniex_post_details(key, pair_name, time_start, time_end, limit)

    err_msg = "get poloniex order history for time interval for pp={pp}".format(pp=post_details)

    status_code, json_document = send_post_request_with_header(post_details, err_msg, max_tries=POLONIEX_NUM_OF_DEAL_RETRY)
    historical_orders = []
    if status_code == STATUS.SUCCESS:
        status_code, historical_orders = get_order_history_poloniex_result_processor(json_document, pair_name)

    return status_code, historical_orders
