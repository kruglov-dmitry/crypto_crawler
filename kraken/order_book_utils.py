from constants import KRAKEN_GET_ORDER_BOOK
from data.OrderBook import OrderBook
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_order_book_kraken_url(currency, timest):
    # https://api.kraken.com/0/public/Depth?pair=XETHXXBT
    final_url = KRAKEN_GET_ORDER_BOOK + currency

    if should_print_debug():
        print final_url

    return final_url


def get_order_book_kraken(currency, timest):

    final_url = get_order_book_kraken_url(currency, timest)

    err_msg = "get_order_book_kraken called for {pair} at {timest}".format(pair=currency, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        if currency in r["result"]:
            return OrderBook.from_kraken(r["result"][currency], currency, timest)

    return None
