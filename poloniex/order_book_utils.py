from constants import POLONIEX_GET_ORDER_BOOK
from data.OrderBook import OrderBook
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_order_book_poloniex(pair_name, timest):
    # https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10, depth optional
    final_url = POLONIEX_GET_ORDER_BOOK + pair_name

    if should_print_debug():
        print final_url

    err_msg = "get_order_book_poloniex called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None:
        return OrderBook.from_poloniex(r, pair_name, timest)

    return None
