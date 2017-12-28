from urllib import urlencode as _urlencode

from data_access.internet import send_post_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from constants import BINANCE_BUY_ORDER, BINANCE_NUM_OF_DEAL_RETRY, BINANCE_DEAL_TIMEOUT

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

    # Yeah, body after that should be empty
    body = {}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "add_buy_order_binance: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_buy_order_binance(key, pair_name, price, amount):

    post_details = add_buy_order_binance_url(key, pair_name, price, amount)

    err_msg = "add_buy_order_binance  called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg,
                                        max_tries=BINANCE_NUM_OF_DEAL_RETRY, timeout=BINANCE_DEAL_TIMEOUT)

    """
    {
        "orderId": 1373289, 
        "clientOrderId": "Is7wGaKBtLBK7JjDkNAJwn",
        "origQty": "10.00000000",
        "symbol": "RDNBTC",
        "side": "BUY",
        "timeInForce": "GTC",
        "status": "NEW",
        "transactTime": 1512581468544,
        "type": "LIMIT",
        "price": "0.00022220",
        "executedQty": "0.00000000"
    }
    """

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res