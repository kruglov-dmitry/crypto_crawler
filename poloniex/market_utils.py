from poloniex.constants import POLONIEX_CANCEL_ORDER
from poloniex.error_handling import is_error
from poloniex.rest_api import send_post_request_with_logging

from data_access.memory_cache import generate_nonce
from data_access.classes.post_request_details import PostRequestDetails

from utils.debug_utils import ERROR_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

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

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_sell_order_poloniex: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel poloniex called for {order_id}".format(order_id=order_id)

    return send_post_request_with_logging(post_details, err_msg)


def parse_order_id_poloniex(json_document):
    """
     {u'orderNumber': u'15573359248', u'resultingTrades': []}
    """

    if is_error(json_document) or "orderNumber" not in json_document:

        msg = "parse_order_id_poloniex - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    return json_document["orderNumber"]
