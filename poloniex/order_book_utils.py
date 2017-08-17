from constants import POLONIEX_GET_ORDER_BOOK
import requests
from data.OrderBook import OrderBook
from debug_utils import should_print_debug


def get_order_book_poloniex(currency, timest):
    # https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10, depth optional
    final_url = POLONIEX_GET_ORDER_BOOK + currency

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url)
        return OrderBook.from_poloniex(r.json(), currency, timest)
    except Exception, e:
        print "get_order_book_poloniex: ", currency, timest, str(e)

    return None
