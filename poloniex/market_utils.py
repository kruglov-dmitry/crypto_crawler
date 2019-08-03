from poloniex.constants import POLONIEX_CANCEL_ORDER, POLONIEX_NUM_OF_DEAL_RETRY, POLONIEX_DEAL_TIMEOUT
from poloniex.error_handling import is_error

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from data_access.classes.post_request_details import PostRequestDetails

from debug_utils import ERROR_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_TRACE

from utils.file_utils import log_to_file
from utils.key_utils import signed_body


def cancel_order_poloniex(key, order_id):
    body = {
        "command": "cancelOrder",
        "orderNumber" : order_id,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CANCEL_ORDER

    post_request = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_sell_order_poloniex: {res}".format(res=post_request)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel poloniex called for {order_id}".format(order_id=order_id)

    res = send_post_request_with_header(post_request, err_msg,
                                        max_tries=POLONIEX_NUM_OF_DEAL_RETRY, timeout=POLONIEX_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_poloniex(json_document):
    """
     {u'orderNumber': u'15573359248', u'resultingTrades': []}
    """

    if is_error(json_document) or "orderNumber" not in json_document:

        msg = "parse_order_id_poloniex - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    return json_document["orderNumber"]
