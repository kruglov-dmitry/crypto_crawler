from urllib import urlencode as _urlencode

from bittrex.constants import BITTREX_BUY_ORDER, BITTREX_DEAL_TIMEOUT

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_get_request_with_header
from data_access.memory_cache import generate_nonce

from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

from utils.file_utils import log_to_file
from utils.key_utils import signed_string
from utils.string_utils import float_to_str


def add_buy_order_bittrex_url(key, pair_name, price, amount):
    # https://bittrex.com/api/v1.1/market/buylimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    final_url = BITTREX_BUY_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "market": pair_name,
        "quantity": float_to_str(amount),
        "rate": float_to_str(price)
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_buy_order_bittrex: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def add_buy_order_bittrex(key, pair_name, price, amount):
    post_details = add_buy_order_bittrex_url(key, pair_name, price, amount)

    err_msg = "add_buy_order bittrex called for {pair} for amount = {amount} " \
              "with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                       timeout=BITTREX_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
