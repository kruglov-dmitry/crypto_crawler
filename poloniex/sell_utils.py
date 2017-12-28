from data_access.memory_cache import generate_nonce
from constants import POLONIEX_SELL_ORDER, POLONIEX_NUM_OF_DEAL_RETRY, POLONIEX_DEAL_TIMEOUT
from data_access.internet import send_post_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from utils.key_utils import signed_body
from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.file_utils import log_to_file


def add_sell_order_poloniex_url(key, pair_name, price, amount):
    body = {
        "command": "sell",
        "currencyPair": pair_name,
        "rate": price,
        "amount": amount,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_SELL_ORDER

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "add_sell_order_poloniex: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_sell_order_poloniex(key, pair_name, price, amount):

    post_details = add_sell_order_poloniex_url(key, pair_name, price, amount)

    err_msg = "add_sell_order poloniex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg,
                                        max_tries=POLONIEX_NUM_OF_DEAL_RETRY, timeout=POLONIEX_DEAL_TIMEOUT)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res