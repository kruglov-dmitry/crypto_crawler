from urllib import urlencode as _urlencode

from binance.constants import BINANCE_SELL_ORDER, BINANCE_NUM_OF_DEAL_RETRY, BINANCE_DEAL_TIMEOUT

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from utils.file_utils import log_to_file
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.string_utils import float_to_str

"""
time in force:
IOC: An immediate or cancel order
GTC: Good-Til-Canceled
"""


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
        "price": float_to_str(price)
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    # Yeah, body after that should be empty
    body = {}

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
    res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=BINANCE_NUM_OF_DEAL_RETRY, timeout=BINANCE_DEAL_TIMEOUT)

    """
    {"orderId": 1373492, "clientOrderId": "e04JGgCpafdrR6O1lOLwgD", "origQty": "1.00000000", "symbol": "RDNBTC", "side": "SELL", "timeInForce": "GTC", "status": "NEW", "transactTime": 1512581721384, "type": "LIMIT", "price": "1.00022220", "executedQty": "0.00000000"}`:w

    """

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res