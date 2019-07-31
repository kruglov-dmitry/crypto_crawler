from poloniex.constants import POLONIEX_GET_OPEN_ORDERS
from poloniex.error_handling import is_error

from data.trade import Trade

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import signed_body


def get_open_orders_poloniex_post_details(key, pair_name):
    body = {
        'command': 'returnOpenOrders',
        'currencyPair': pair_name,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_OPEN_ORDERS

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_open_order_poloniex: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_poloniex(key, pair_name):
    post_details = get_open_orders_poloniex_post_details(key, pair_name)

    err_msg = "get poloniex open orders"

    status_code, res = send_post_request_with_header(post_details, err_msg, max_tries=3)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_open_orders_poloniex: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, "market_utils.log")

    orders = []
    if status_code == STATUS.SUCCESS:
        status_code, orders = get_open_orders_poloniex_result_processor(res, pair_name)

    return status_code, orders


def get_open_orders_poloniex_result_processor(json_document, pair_name):
    orders = []
    if is_error(json_document):

        msg = "get_open_orders_poloniex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document:
        order = Trade.from_poloniex(entry, pair_name)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders
