from constants import BINANCE_CANCEL_ORDER, BINANCE_BUY_ORDER, BINANCE_SELL_ORDER, BINANCE_CHECK_BALANCE
from debug_utils import should_print_debug
from utils.key_utils import signed_string, generate_nonce
from data_access.internet import send_post_request_with_header, send_delete_request_with_header
from urllib import urlencode as _urlencode
from data.Balance import Balance
from utils.time_utils import get_now_seconds_local
from enums.status import STATUS

"""
time in force:
IOC: An immediate or cancel order
GTC: Good-Til-Canceled
"""


def add_buy_order_binance(key, pair_name, price, amount):
    #  curl -H "X-MBX-APIKEY: vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
    # -X POST 'https://api.binance.com/api/v3/order' -d 'symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1
    # &price=0.1&recvWindow=6000000&timestamp=1499827319559&signature=c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71'
    final_url = BINANCE_BUY_ORDER + "&timestamp=" + str(generate_nonce())

    body = {
        "symbol": pair_name,
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "recvWindow": 5000,
        "quantity": amount,
        "price": price
    }

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key, "signature": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order_binance  called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def add_sell_order_binance(key, pair_name, price, amount):

    final_url = BINANCE_SELL_ORDER + "&timestamp=" + str(generate_nonce())

    body = {
        "symbol": pair_name,
        "side": "SELL",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "recvWindow": 5000,
        "quantity": amount,
        "price": price
    }

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key, "signature": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order binance called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def cancel_order_binance(key, pair_name, deal_id):

    final_url = BINANCE_CANCEL_ORDER + "&timestamp=" + str(generate_nonce())

    body = {
        "symbol": pair_name,
        "orderId": deal_id
    }

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key, "signature": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel binance order with id {id}".format(id=deal_id)

    res = send_delete_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def get_balance_binance(key):
    """
        https://bittrex.com/api/v1.1/account/getbalances?apikey=8a2dd16465b0469197574ec0a516badb&nonce=1508507525325
        {'apisign': 'e6bfb1cc60dcd93d291542cf6c4084e942659be7c363633f710336338a3158b37eb3f999250e5113ffc9e48c18ebe24cf9f4d496f6348a319cbd7f1bc0fc680c'} {}
        {u'message': u'',
        u'result': [{u'Available': 21300.0, u'Currency': u'ARDR', u'Balance': 21300.0, u'Pending': 0.0,
        u'CryptoAddress': u'76730d86115b49b9b7f71578feb35b7da1ca6c13e5f745aa9b630707f5439e68'},

        {u'Available': 49704.04069438, u'Currency': u'BAT', u'Balance': 49704.04069438, u'Pending': 0.0,
        u'CryptoAddress': None},

        {u'Available': 0.0, u'Currency': u'BCC', u'Balance': 0.0, u'Pending': 0.0,
        u'CryptoAddress': u'1H24rzfFWy8thV1AYQch3GByrQQuXA65LY'},

        {u'Available': 0.28912516, u'Currency': u'BTC', u'Balance': 0.28912516, u'Pending': 0.0,
        u'CryptoAddress': u'1EJztGvnKbNj3GeFbt83HhsKeLBYeu8jGq'},

        {u'Available': 0.0, u'Currency': u'BTS', u'Balance': 0.0, u'Pending': 0.0, u'CryptoAddress': u'490d0054055c43ada6e'},

    """

    final_url = BINANCE_CHECK_BALANCE + "&timestamp=" + str(generate_nonce())

    body = {
    }

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key, "signature": signed_string(final_url, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check binance balance called"

    timest = get_now_seconds_local()

    error_code, res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if error_code == STATUS.SUCCESS and res is not None:
        res = Balance.from_binance(timest, res)

    return error_code, res
