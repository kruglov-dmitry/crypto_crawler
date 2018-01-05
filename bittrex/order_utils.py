from urllib import urlencode as _urlencode

from bittrex.constants import BITTREX_NUM_OF_DEAL_RETRY, BITTREX_DEAL_TIMEOUT, BITTREX_GET_OPEN_ORDERS

from data.Trade import Trade

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import signed_string


def get_open_orders_bittrix_post_details(key, pair_name):
    final_url = BITTREX_GET_OPEN_ORDERS + key.api_key + "&nonce=" + str(generate_nonce())

    body = {"market": pair_name} if pair_name is not None else {}

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "get_open_orders_bittrix: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_bittrix(key, pair_name):

    post_details = get_open_orders_bittrix_post_details(key, pair_name)

    err_msg = "get_orders_binance"

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=BITTREX_NUM_OF_DEAL_RETRY,
                                                    timeout=BITTREX_DEAL_TIMEOUT)

    print "get_open_orders_bittrix", res
    orders = []
    if error_code == STATUS.SUCCESS and res is not None and "result" in res:
        orders = get_open_orders_bittrex_result_processor(res["result"])

    return error_code, orders


def get_open_orders_bittrex_result_processor(json_document):
    orders = []
    if json_document is not None:
        for entry in json_document:
            order = Trade.from_bittrex(entry)
            if order is not None:
                orders.append(order)

    return orders
