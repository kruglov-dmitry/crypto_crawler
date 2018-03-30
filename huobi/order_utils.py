from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_NUM_OF_DEAL_RETRY, HUOBI_DEAL_TIMEOUT, HUOBI_GET_OPEN_ORDERS
from huobi.error_handling import is_error

from data.Trade import Trade

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import ERROR_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import signed_string


def get_open_orders_huobi_post_details(key, pair_name):
    final_url = HUOBI_GET_OPEN_ORDERS + key.api_key + "&nonce=" + str(generate_nonce())

    body = {"symbol": pair_name} if pair_name is not None else {}

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_open_orders_huobi: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_huobi(key, pair_name):

    post_details = get_open_orders_huobi_post_details(key, pair_name)

    err_msg = "get_orders_huobi"

    status_code, res = send_post_request_with_header(post_details, err_msg, max_tries=HUOBI_NUM_OF_DEAL_RETRY,
                                                     timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_open_orders_huobi: {r}".format(r=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    orders = []
    if status_code == STATUS.SUCCESS:
        status_code, orders = get_open_orders_huobi_result_processor(res, pair_name)

    return status_code, orders


def get_open_orders_huobi_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """

    orders = []
    if is_error(json_document) or "data" not in json_document:

        msg = "get_open_orders_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document["data"]:
        order = Trade.from_huobi(entry, pair_name)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders