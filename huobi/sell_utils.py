import json

from huobi.constants import HUOBI_SELL_ORDER, HUOBI_API_URL, HUOBI_API_ONLY, HUOBI_POST_HEADERS
from huobi.account_utils import get_huobi_account
from huobi.rest_api import generate_body_and_url_get_request, send_post_request_with_logging

from data_access.classes.post_request_details import PostRequestDetails
from utils.string_utils import float_to_str

SELL_URL = HUOBI_API_URL + HUOBI_SELL_ORDER + "?"


def add_sell_order_huobi_url(key, pair_name, price, amount):

    final_url = SELL_URL + generate_body_and_url_get_request(key, HUOBI_API_ONLY, HUOBI_SELL_ORDER)

    params = json.dumps({
        'amount': float_to_str(amount),
        'price': float_to_str(price),
        'symbol': pair_name,
        'source': 'api',
        'type': 'sell-limit',
        'account-id': get_huobi_account(key),
    })

    res = PostRequestDetails(final_url, HUOBI_POST_HEADERS, params)

    return res


def add_sell_order_huobi(key, pair_name, price, amount):
    post_details = add_sell_order_huobi_url(key, pair_name, price, amount)

    err_msg = "add_sell_order huobi called for {pair} for amount = {amount} with price {price}".format(
        pair=pair_name, amount=amount, price=price)

    return send_post_request_with_logging(post_details, err_msg)
