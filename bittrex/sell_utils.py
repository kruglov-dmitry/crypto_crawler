from urllib import urlencode as _urlencode

from bittrex.constants import BITTREX_SELL_ORDER, BITTREX_NUM_OF_DEAL_RETRY, BITTREX_DEAL_TIMEOUT

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from utils.file_utils import log_to_file
from utils.key_utils import signed_string


def add_sell_order_bittrex_url(key, pair_name, price, amount):
    # https://bittrex.com/api/v1.1/market/selllimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    final_url = BITTREX_SELL_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "market": pair_name,
        "quantity": amount,
        "rate": price
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "add_sell_order_bittrex: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_sell_order_bittrex(key, pair_name, price, amount):

    post_details = add_sell_order_bittrex_url(key, pair_name, price, amount)

    err_msg = "add_sell_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=BITTREX_NUM_OF_DEAL_RETRY, timeout=BITTREX_DEAL_TIMEOUT)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res