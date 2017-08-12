from constants import KRAKEN_GET_ORDER_BOOK
import requests
from data.OrderBook import OrderBook
from daemon import should_print_debug

def get_order_book_kraken(currency, timest):
    # https://api.kraken.com/0/public/Depth?pair=XETHXXBT
    final_url = KRAKEN_GET_ORDER_BOOK + currency

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        if "result" in r:
            return OrderBook.from_kraken(r["result"][currency], currency, timest)
    except Exception, e:
        print "get_order_book_kraken: ", currency, timest, str(e)

    return None
