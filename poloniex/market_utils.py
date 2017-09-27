from constants import POLONIEX_CANCEL_ORDER, POLONIEX_BUY_ORDER, POLONIEX_SELL_ORDER
from data_access.internet import send_post_request_with_header
import time
from debug_utils import should_print_debug
from utils.key_utils import get_key_by_exchange
import hmac
import hashlib
from urllib import urlencode as _urlencode


def generate_nonce():
    # Additionally, all queries must include a "nonce" POST parameter.
    # The nonce parameter is an integer which must always be greater than the previous nonce used.
    # FIXME - store in db
    return int(round(time.time() * 1000))


def signed_body(body):
    key = get_key_by_exchange("poloniex")
    #  The query's POST data signed by your key's "secret" according to the HMAC-SHA512 method.
    payload = hmac.new(key.secret, _urlencode(body), hashlib.sha512).hexdigest()

    return payload


def add_buy_order_poloniex(key, pair_name, price, amount):
    body = {
        "command": "buy",
        "currencyPair": pair_name,
        "rate": price,
        "amount": amount,
        "nonce": generate_nonce()
    }

    headers = {"Key": key, "Sign": signed_body(body)}
    # https://poloniex.com/tradingApi
    final_url = POLONIEX_BUY_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order poloniex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def add_sell_order_poloniex(key, pair_name, price, amount):
    body = {
        "command": "sell",
        "currencyPair": pair_name,
        "rate": price,
        "amount": amount,
        "nonce": generate_nonce()
    }

    headers = {"Key": key, "Sign": signed_body(body)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_SELL_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order poloniex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def cancel_order_poloniex(key, deal_id):
    body = {
        "command": "cancelOrder",
        "orderNumber" : deal_id,
        "nonce": generate_nonce()
    }

    headers = {"Key": key, "Sign": signed_body(body)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CANCEL_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel poloniex called for {deal_id}".format(deal_id=deal_id)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r
