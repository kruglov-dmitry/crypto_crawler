from constants import BITTREX_GET_ORDER_BOOK
from data.OrderBook import OrderBook
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_order_book_bittrex(currency, timest):
    # https://bittrex.com/api/v1.1/public/getorderbook?type=both&market=BTC-LTC
    final_url = BITTREX_GET_ORDER_BOOK + currency

    if should_print_debug():
        print final_url

    err_msg = "get_order_book_bittrex called for {pair} at {timest}".format(pair=currency, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        return OrderBook.from_bittrex(r["result"], currency, timest)

    return None
