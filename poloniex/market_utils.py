from constants import POLONIEX_CANCEL_ORDER, POLONIEX_GET_ORDER_HISTORY, POLONIEX_NUM_OF_DEAL_RETRY, \
    POLONIEX_DEAL_TIMEOUT
from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.file_utils import log_to_file
from utils.key_utils import signed_body


def cancel_order_poloniex(key, deal_id):
    body = {
        "command": "cancelOrder",
        "orderNumber" : deal_id,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CANCEL_ORDER

    if should_print_debug():
        msg = "add_sell_order_poloniex: url - {url} headers - {headers} body - {body}".format(url=final_url,
                                                                                            headers=headers, body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel poloniex called for {deal_id}".format(deal_id=deal_id)

    res = send_post_request_with_header(final_url, headers, body, err_msg,
                                        max_tries=POLONIEX_NUM_OF_DEAL_RETRY, timeout=POLONIEX_DEAL_TIMEOUT)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_deal_id_poloniex(json_document):
    """
     {u'orderNumber': u'15573359248', u'resultingTrades': []}
    """
    if json_document is not None and "orderNumber" in json_document:
        return json_document["orderNumber"]

    return None


def get_order_history_poloniex_post_details(key, currency_name):
    body = {
        'command': 'returnTradeHistory',
        'currencyPair': currency_name,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_ORDER_HISTORY

    res = PostRequestDetails(final_url, headers, body)

    # if should_print_debug():
    #    print res

    return res


def get_orders_history_poloniex(key, currency_name):
    post_details = get_order_history_poloniex_post_details(key, currency_name)

    err_msg = "get poloniex order history"

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=3)

    return error_code, res
