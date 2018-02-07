from urllib import urlencode as _urlencode
from bittrex.constants import BITTREX_GET_TRADE_HISTORY, BITTREX_NUM_OF_DEAL_RETRY
from data_access.classes.PostRequestDetails import PostRequestDetails

from data.Trade import Trade
from enums.status import STATUS

from utils.key_utils import signed_string
from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.file_utils import log_to_file

from data_access.memory_cache import generate_nonce
from data_access.internet import send_post_request_with_header


def get_order_history_binance_post_details(key, pair_name):
    final_url = BITTREX_GET_TRADE_HISTORY + key.api_key + "&nonce=" + str(generate_nonce())

    if pair_name != "all":
        body = {"market": pair_name}
    else:
        body = {}

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    post_details = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "get_open_orders_binance: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_bittrex_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """
    orders = []
    if json_document is None or "result" not in json_document:
        return orders

    for entry in json_document["result"]:
        order = Trade.from_bittrex_history(entry)
        if order is not None:
            orders.append(order)

    return orders


def get_order_history_bittrex(key, pair_name):

    post_details = get_order_history_binance_post_details(key, pair_name)

    err_msg = "get bittrex order history for time interval for pp={pp}".format(pp=post_details)

    error_code, json_responce = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=BITTREX_NUM_OF_DEAL_RETRY)

    historical_orders = []
    if error_code == STATUS.SUCCESS:
        historical_orders = get_order_history_bittrex_result_processor(json_responce, pair_name)

    return error_code, historical_orders
