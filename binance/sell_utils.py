from binance.constants import BINANCE_SELL_ORDER, BINANCE_NUM_OF_DEAL_RETRY, BINANCE_DEAL_TIMEOUT
from binance.rest_api import generate_post_request

from data_access.internet import send_post_request_with_header

from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

from utils.file_utils import log_to_file
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

    res = generate_post_request(final_url, body, key)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_sell_order_binance: url - {url} headers - {headers} body - {body}".format(url=res.final_url,
                                                                                             headers=res.headers,
                                                                                             body=res.body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_sell_order_binance(key, pair_name, price, amount):

    post_details = add_sell_order_binance_url(key, pair_name, price, amount)

    err_msg = "add_sell_order binance called for {pair} for amount = {amount} " \
              "with price {price}".format(pair=pair_name, amount=amount, price=price)

    # NOTE: Yeah, body must be empty!
    res = send_post_request_with_header(post_details, err_msg, max_tries=BINANCE_NUM_OF_DEAL_RETRY, timeout=BINANCE_DEAL_TIMEOUT)

    """
    {
        "orderId": 1373492, 
        "clientOrderId": "e04JGgCpafdrR6O1lOLwgD",
        "origQty": "1.00000000",
        "symbol": "RDNBTC",
        "side": "SELL",
        "timeInForce": "GTC",
        "status": "NEW",
        "transactTime": 1512581721384,
        "type": "LIMIT",
        "price": "1.00022220",
        "executedQty": "0.00000000"
    }
    """

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
