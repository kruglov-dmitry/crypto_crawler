from constants import KRAKEN_CANCEL_ORDER, KRAKEN_BUY_ORDER, KRAKEN_SELL_ORDER, KRAKEN_CHECK_BALANCE
from data_access.internet import send_post_request_with_header
from debug_utils import should_print_debug
from utils.key_utils import generate_nonce, signed_body


def add_buy_order_kraken(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_BUY_ORDER

    current_nonce = generate_nonce()

    body = {
        "pair": pair_name,
        "type": "buy",
        "ordertype": "market",
        "price": "price",
        "volume": "amount",
        "nonce": current_nonce
    }

    headers = {"API-Key": key.api_key, "API-Sign": signed_body(body, key.secret) }

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)

    print r


def add_sell_order_kraken(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_SELL_ORDER

    current_nonce = generate_nonce()

    body = {
        "pair": pair_name,
        "type": "sell",
        "ordertype": "market",
        "price": "price",
        "volume": "amount",
        "nonce": current_nonce
    }

    headers = {"API-Key": key.api_key, "API-Sign": signed_body(body, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)

    print r


def cancel_order_kraken(key, deal_id):
    # https://api.kraken.com/0/private/CancelOrder
    final_url = KRAKEN_CANCEL_ORDER

    body = {
        "txid": deal_id,
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": signed_body(body, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel kraken called for {deal_id}".format(deal_id=deal_id)

    r = send_post_request_with_header(final_url, headers, body, err_msg)

    print r


def show_balance_bittrex(key):

    final_url = KRAKEN_CHECK_BALANCE

    body = {
        "nonce=": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": signed_body(body, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check kraken balance called"

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r