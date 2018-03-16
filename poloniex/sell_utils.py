from poloniex.constants import POLONIEX_SELL_ORDER, POLONIEX_NUM_OF_DEAL_RETRY, POLONIEX_DEAL_TIMEOUT

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

from utils.file_utils import log_to_file
from utils.key_utils import signed_body
from utils.string_utils import float_to_str


def add_sell_order_poloniex_url(key, pair_name, price, amount):
    body = {
        "command": "sell",
        "currencyPair": pair_name,
        "rate": float_to_str(price),
        "amount": float_to_str(amount),
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_SELL_ORDER

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_sell_order_poloniex: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_sell_order_poloniex(key, pair_name, price, amount):

    post_details = add_sell_order_poloniex_url(key, pair_name, price, amount)

    err_msg = "add_sell_order poloniex called for {pair} for amount = {amount} with price {price}".format(
        pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(post_details, err_msg, max_tries=POLONIEX_NUM_OF_DEAL_RETRY, timeout=POLONIEX_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res