from poloniex.constants import POLONIEX_SELL_ORDER
from poloniex.rest_api import generate_body, send_post_request_with_logging

from data_access.classes.post_request_details import PostRequestDetails

from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

from utils.file_utils import log_to_file
from utils.key_utils import signed_body


def add_sell_order_poloniex_url(key, pair_name, price, amount):
    body = generate_body(pair_name, price, amount, "sell")

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

    return send_post_request_with_logging(post_details, err_msg)
