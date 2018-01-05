from binance.constants import BINANCE_GET_ORDER_BOOK

from data.OrderBook import OrderBook

from debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG

from data_access.internet import send_request

from enums.status import STATUS


def get_order_book_binance_url(currency, timest):
    # https://api.binance.com/api/v1/depth?symbol=XMRETH
    final_url = BINANCE_GET_ORDER_BOOK + currency

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_order_book_binance(currency, timest):

    final_url = get_order_book_binance_url(currency, timest)

    err_msg = "get_order_book_binance called for {pair} at {timest}".format(pair=currency, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None:
        return OrderBook.from_binance(r, currency, timest)

    return None


def get_order_book_binance_result_processor(json_document, pair_name, timest):
    if json_document is not None:
        return OrderBook.from_binance(json_document, pair_name, timest)

    return None
