from constants import BITTREX_CANCEL_ORDER, BITTREX_BUY_ORDER, BITTREX_SELL_ORDER, BITTREX_CHECK_BALANCE
from debug_utils import should_print_debug
from utils.key_utils import generate_nonce, signed_body
from data_access.internet import send_post_request_with_header


def add_buy_order_bittrex(key, pair_name, price, amount):
    # https://bittrex.com/api/v1.1/market/buylimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    final_url = BITTREX_BUY_ORDER # \
    # + key + "&market=" + pair_name + "&quantity=" + str(amount) + "&rate=" + str(price)

    body = {
        "apikey": key.api_key,
        "market": pair_name,
        "quantity": amount,
        "rate": price,
        "nonce": generate_nonce()
    }

    headers = {"apisign": signed_body(body, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def add_sell_order_bittrex(key, pair_name, price, amount):
    # https://bittrex.com/api/v1.1/market/selllimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    final_url = BITTREX_SELL_ORDER # + key + "&market=" + pair_name + "&quantity=" + str(amount) + "&rate=" + str(price)

    body = {
        "apikey": key.api_key,
        "market": pair_name,
        "quantity": amount,
        "rate": price,
        "nonce": generate_nonce()
    }

    headers = {"apisign": signed_body(body, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def cancel_order_bittrex(key, deal_id):
    # https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
    final_url = BITTREX_CANCEL_ORDER # + key + "&uuid=" + deal_id

    body = {
        "apikey": key.api_key,
        "uuid": deal_id,
        "nonce": generate_nonce()
    }

    headers = {"apisign": signed_body(body, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel bittrex order with id {id}".format(id=deal_id)

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r


def show_balance_bittrex(key):
    # https://poloniex.com/tradingApi
    final_url = BITTREX_CHECK_BALANCE + key + "&nonce=" + generate_nonce()

    body = {
    }

    headers = {"apisign": signed_body(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check bittrex balance called"

    r = send_post_request_with_header(final_url, headers, body, err_msg)
    print r
