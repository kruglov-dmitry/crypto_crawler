from constants import BINANCE_CANCEL_ORDER, BINANCE_BUY_ORDER, BINANCE_SELL_ORDER, BINANCE_CHECK_BALANCE
from debug_utils import should_print_debug
from utils.key_utils import signed_body_256, signed_string, generate_nonce
from data_access.internet import send_get_request_with_header, send_post_request_with_header, send_delete_request_with_header
from urllib import urlencode as _urlencode
from data.Balance import Balance
from utils.time_utils import get_now_seconds_utc
from enums.status import STATUS
from data_access.PostRequestDetails import PostRequestDetails

"""
time in force:
IOC: An immediate or cancel order
GTC: Good-Til-Canceled
"""


def add_buy_order_binance(key, pair_name, price, amount):
    #  curl -H "X-MBX-APIKEY: vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
    # -X POST 'https://api.binance.com/api/v3/order' -d 'symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1
    # &price=0.1&recvWindow=6000000&timestamp=1499827319559&signature=c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71'
    final_url = BINANCE_BUY_ORDER

    body = {
        "symbol": pair_name,
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "recvWindow": 5000,
        "timestamp": generate_nonce(),
        "quantity": amount,
        "price": price
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order_binance  called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, {}, err_msg, max_tries=3)

    """
    {"orderId": 1373289, "clientOrderId": "Is7wGaKBtLBK7JjDkNAJwn", "origQty": "10.00000000", "symbol": "RDNBTC", "side": "BUY", "timeInForce": "GTC", "status": "NEW", "transactTime": 1512581468544, "type": "LIMIT", "price": "0.00022220", "executedQty": "0.00000000"}

    """


    if should_print_debug():
        print res

    return res


def add_sell_order_binance(key, pair_name, price, amount):

    final_url = BINANCE_SELL_ORDER

    body = {
        "symbol": pair_name,
        "side": "SELL",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "recvWindow": 5000,
        "timestamp": generate_nonce(),
        "quantity": amount,
        "price": price
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order binance called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, {}, err_msg, max_tries=3)

    """
    {"orderId": 1373492, "clientOrderId": "e04JGgCpafdrR6O1lOLwgD", "origQty": "1.00000000", "symbol": "RDNBTC", "side": "SELL", "timeInForce": "GTC", "status": "NEW", "transactTime": 1512581721384, "type": "LIMIT", "price": "1.00022220", "executedQty": "0.00000000"}`:w

    """

    if should_print_debug():
        print res

    return res


def cancel_order_binance(key, pair_name, deal_id):

    final_url = BINANCE_CANCEL_ORDER

    body = {
        "recvWindow": 5000,
        "timestamp": generate_nonce(),
        "symbol": pair_name,
        "orderId": deal_id
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel binance order with id {id}".format(id=deal_id)

    res = send_delete_request_with_header(final_url, headers, {}, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def get_balance_binance_post_details(key):
    final_url = BINANCE_CHECK_BALANCE

    body = {
        "timestamp": generate_nonce(),
        "recvWindow": 5000
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print res

    return res


def get_balance_binance_result_processor(json_document, timest):
    if json_document is not None:
        return Balance.from_binance(timest, json_document)

    return None


def get_balance_binance(key):
    """

    """

    post_details = get_balance_binance_post_details(key)

    err_msg = "check binance balance called"

    timest = get_now_seconds_utc()

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg)

    if error_code == STATUS.SUCCESS and res is not None:
        res = Balance.from_binance(timest, res)

    return error_code, res
