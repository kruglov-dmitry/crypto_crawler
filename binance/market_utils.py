from urllib import urlencode as _urlencode

from data_access.internet import send_get_request_with_header, send_post_request_with_header, \
    send_delete_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from data.Balance import Balance

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, \
    LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc, get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from constants import BINANCE_CANCEL_ORDER, BINANCE_BUY_ORDER, BINANCE_SELL_ORDER, BINANCE_CHECK_BALANCE, \
    BINANCE_NUM_OF_DEAL_RETRY, BINANCE_DEAL_TIMEOUT
from enums.status import STATUS

"""
time in force:
IOC: An immediate or cancel order
GTC: Good-Til-Canceled
"""


def add_buy_order_binance_url(key, pair_name, price, amount):
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
        "timestamp": get_now_seconds_utc_ms(),
        "quantity": amount,
        "price": price
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "add_buy_order_binance: url - {url} headers - {headers} body - {body}".format(url=res.final_url, headers=res.headers, body=res.body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_buy_order_binance(key, pair_name, price, amount):

    post_details = add_buy_order_binance_url(key, pair_name, price, amount)

    err_msg = "add_buy_order_binance  called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    # NOTE: Yeah, body must be empty!
    res = send_post_request_with_header(post_details.final_url, post_details.headers, {}, err_msg, max_tries=BINANCE_NUM_OF_DEAL_RETRY, timeout=BINANCE_DEAL_TIMEOUT)

    """
    {"orderId": 1373289, "clientOrderId": "Is7wGaKBtLBK7JjDkNAJwn", "origQty": "10.00000000", "symbol": "RDNBTC", "side": "BUY", "timeInForce": "GTC", "status": "NEW", "transactTime": 1512581468544, "type": "LIMIT", "price": "0.00022220", "executedQty": "0.00000000"}

    """

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def add_sell_order_binance_url(key, pair_name, price, amount):

    final_url = BINANCE_SELL_ORDER

    body = {
        "symbol": pair_name,
        "side": "SELL",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "recvWindow": 5000,
        "timestamp": get_now_seconds_utc_ms(),
        "quantity": amount,
        "price": price
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "add_sell_order_binance: url - {url} headers - {headers} body - {body}".format(url=res.final_url,
                                                                                             headers=res.headers,
                                                                                             body=res.body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_sell_order_binance(key, pair_name, price, amount):

    post_details = add_sell_order_binance_url(key, pair_name, price, amount)

    err_msg = "add_sell_order binance called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    # NOTE: Yeah, body must be empty!
    res = send_post_request_with_header(post_details.final_url, post_details.headers, {}, err_msg, max_tries=BINANCE_NUM_OF_DEAL_RETRY, timeout=BINANCE_DEAL_TIMEOUT)

    """
    {"orderId": 1373492, "clientOrderId": "e04JGgCpafdrR6O1lOLwgD", "origQty": "1.00000000", "symbol": "RDNBTC", "side": "SELL", "timeInForce": "GTC", "status": "NEW", "transactTime": 1512581721384, "type": "LIMIT", "price": "1.00022220", "executedQty": "0.00000000"}`:w

    """

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def cancel_order_binance(key, pair_name, deal_id):

    final_url = BINANCE_CANCEL_ORDER

    body = {
        "recvWindow": 5000,
        "timestamp": get_now_seconds_utc(),
        "symbol": pair_name,
        "orderId": deal_id
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    if should_print_debug():
        msg = "cancel_order_binance: url - {url} headers - {headers} body - {body}".format(url=final_url,
                                                                                             headers=headers,
                                                                                             body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel binance order with id {id}".format(id=deal_id)

    res = send_delete_request_with_header(final_url, headers, {}, err_msg, max_tries=3)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def get_balance_binance_post_details(key):
    final_url = BINANCE_CHECK_BALANCE

    body = {
        "timestamp": get_now_seconds_utc_ms(),
        "recvWindow": 5000
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_binance_result_processor(json_document, timest):
    if json_document is not None and "balances" in json_document:
        return Balance.from_binance(timest, json_document)

    return None


def get_balance_binance(key):
    """

    """

    post_details = get_balance_binance_post_details(key)

    err_msg = "check binance balance called"

    timest = get_now_seconds_utc()

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg)

    if error_code == STATUS.SUCCESS and res is not None and "balances" in res:
        res = Balance.from_binance(timest, res)

    return error_code, res
