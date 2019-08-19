from urllib import urlencode as _urlencode

from bittrex.constants import BITTREX_GET_TRADE_HISTORY, BITTREX_NUM_OF_DEAL_RETRY
from bittrex.error_handling import is_error

from data_access.classes.post_request_details import PostRequestDetails

from data.trade import Trade
from enums.status import STATUS

from utils.key_utils import signed_string
from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

from data_access.memory_cache import generate_nonce
from data_access.internet import send_get_request_with_header


def get_order_history_bittrex_post_details(key, pair_name):
    final_url = BITTREX_GET_TRADE_HISTORY + key.api_key + "&nonce=" + str(generate_nonce())

    if pair_name != "all":
        body = {"market": pair_name}
    else:
        body = {}

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_order_history_bittrex_post_details: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_bittrex_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """

    orders = []
    if is_error(json_document) or json_document["result"] is None:

        msg = "get_order_history_bittrex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document["result"]:
        order = Trade.from_bittrex_history(entry)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders


def get_order_history_bittrex(key, pair_name):

    post_details = get_order_history_bittrex_post_details(key, pair_name)

    err_msg = "get bittrex order history for time interval for pp={pp}".format(pp=post_details)

    status_code, json_response = send_get_request_with_header(post_details.final_url,
                                                              post_details.headers,
                                                              err_msg)

    historical_orders = []
    if status_code == STATUS.SUCCESS:
        status_code, historical_orders = get_order_history_bittrex_result_processor(json_response, pair_name)

    return status_code, historical_orders
