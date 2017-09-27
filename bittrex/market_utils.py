from constants import BITTREX_CANCEL_ORDER, BITTREX_BUY_ORDER, BITTREX_SELL_ORDER, BITTREX_CHECK_BALANCE
from debug_utils import should_print_debug
from utils.key_utils import signed_string, generate_nonce
from data_access.internet import send_post_request_with_header
from urllib import urlencode as _urlencode


def add_buy_order_bittrex(key, pair_name, price, amount):
    # https://bittrex.com/api/v1.1/market/buylimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    final_url = BITTREX_BUY_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "market": pair_name,
        "quantity": amount,
        "rate": price
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def add_sell_order_bittrex(key, pair_name, price, amount):
    # https://bittrex.com/api/v1.1/market/selllimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    final_url = BITTREX_SELL_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "market": pair_name,
        "quantity": amount,
        "rate": price
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def cancel_order_bittrex(key, deal_id):
    # https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
    final_url = BITTREX_CANCEL_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "uuid": deal_id,
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel bittrex order with id {id}".format(id=deal_id)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def show_balance_bittrex(key):

    final_url = BITTREX_CHECK_BALANCE + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
    }

    final_url += _urlencode(body)

    print final_url, type(final_url)

    headers = {"apisign": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check bittrex balance called"

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r
