from urllib import urlencode as _urlencode

from bittrex.constants import BITTREX_NUM_OF_DEAL_RETRY, BITTREX_DEAL_TIMEOUT, BITTREX_GET_OPEN_ORDERS
from bittrex.error_handling import is_error

from data.trade import Trade

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import ERROR_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import signed_string


def get_open_orders_bittrix_post_details(key, pair_name):
    final_url = BITTREX_GET_OPEN_ORDERS + key.api_key + "&nonce=" + str(generate_nonce())

    body = {"market": pair_name} if pair_name is not None else {}

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_open_orders_bittrix: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_bittrix(key, pair_name):

    post_details = get_open_orders_bittrix_post_details(key, pair_name)

    err_msg = "get_orders_bittrix"

    status_code, res = send_post_request_with_header(post_details, err_msg, max_tries=BITTREX_NUM_OF_DEAL_RETRY,
                                                     timeout=BITTREX_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_open_orders_bittrix: {r}".format(r=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    orders = []
    if status_code == STATUS.SUCCESS:
        status_code, orders = get_open_orders_bittrex_result_processor(res, pair_name)

    return status_code, orders


def get_open_orders_bittrex_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """

    orders = []
    if is_error(json_document):

        msg = "get_open_orders_bittrex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document["result"]:
        order = Trade.from_bittrex(entry)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders
