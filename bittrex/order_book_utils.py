from constants import BITTREX_GET_ORDER_BOOK
import requests
from data.OrderBook import OrderBook
from debug_utils import should_print_debug


def get_order_book_bittrex(currency, timest):
    # https://bittrex.com/api/v1.1/public/getorderbook?type=both&market=BTC-LTC
    final_url = BITTREX_GET_ORDER_BOOK + currency

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        if "result" in r:
            return OrderBook.from_bittrex(r["result"], currency, timest)
    except Exception, e:
        print "get_order_book_bittrex: ", currency, timest, str(e)

    return None
