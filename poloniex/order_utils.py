from data_access.memory_cache import generate_nonce
from constants import POLONIEX_GET_OPEN_ORDERS
from data_access.internet import send_post_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.file_utils import log_to_file

from enums.status import STATUS
from data.Trade import Trade

from utils.key_utils import signed_body


def get_open_orders_poloniex_post_details(key, currency_name):
    body = {
        'command': 'returnOpenOrders',
        'currencyPair': currency_name,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_OPEN_ORDERS

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "get_open_order_poloniex: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_poloniex(key, currency_name):
    post_details = get_open_orders_poloniex_post_details(key, currency_name)

    err_msg = "get poloniex open orders"
    print err_msg

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=3)

    print res
    orders = []
    if error_code == STATUS.SUCCESS and res is not None:
        orders = get_open_orders_poloniex_result_processor(res)

    return error_code, orders


def get_open_orders_poloniex_result_processor(json_document):
    orders = []
    if json_document is not None:
        for entry in json_document:
            order = Trade.from_poloniex(entry)
            if order is not None:
                orders.append(order)

    return orders
