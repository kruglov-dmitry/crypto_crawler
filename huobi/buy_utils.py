import json

from huobi.constants import HUOBI_BUY_ORDER, HUOBI_API_URL, HUOBI_API_ONLY, \
    HUOBI_POST_HEADERS
from huobi.account_utils import get_huobi_account

from data_access.classes.post_request_details import PostRequestDetails

from debug_utils import get_logging_level, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from utils.file_utils import log_to_file
from utils.string_utils import float_to_str
from huobi.rest_api import generate_body_and_url_get_request, send_post_request_with_logging

BUY_URL = HUOBI_API_URL + HUOBI_BUY_ORDER + "?"


def add_buy_order_huobi_url(key, pair_name, price, amount):

    final_url = BUY_URL + generate_body_and_url_get_request(key, HUOBI_API_ONLY, HUOBI_BUY_ORDER)

    params = json.dumps({
        "account-id": get_huobi_account(key),
        "amount": float_to_str(amount),
        "price": float_to_str(price),
        "source": "api",
        "symbol": pair_name,
        "type": "buy-limit"
    })

    res = PostRequestDetails(final_url, HUOBI_POST_HEADERS, params)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_buy_order_huobi: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_buy_order_huobi(key, pair_name, price, amount):

    post_details = add_buy_order_huobi_url(key, pair_name, price, amount)

    err_msg = "add_buy_order_huobi  called for {pair} for amount = {amount} with price {price}".format(
        pair=pair_name, amount=amount, price=price)

    return send_post_request_with_logging(post_details, err_msg)
