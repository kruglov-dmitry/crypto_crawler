from utils.key_utils import generate_nonce, signed_body
from constants import POLONIEX_CANCEL_ORDER, POLONIEX_BUY_ORDER, POLONIEX_SELL_ORDER, POLONIEX_CHECK_BALANCE
from data_access.internet import send_post_request_with_header
from debug_utils import should_print_debug


def add_buy_order_poloniex(key, pair_name, price, amount):
    body = {
        "command": "buy",
        "currencyPair": pair_name,
        "rate": price,
        "amount": amount,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}
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

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

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

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CANCEL_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel poloniex called for {deal_id}".format(deal_id=deal_id)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def show_balance_poloniex(key):
    body = {
        'command': 'returnBalances',
        'nonce': generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CHECK_BALANCE

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check poloniex balance called"

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r