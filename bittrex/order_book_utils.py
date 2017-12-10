from constants import BITTREX_GET_ORDER_BOOK
from data.OrderBook import OrderBook
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_order_book_bittrex_url(pair_name, timest):
    # https://bittrex.com/api/v1.1/public/getorderbook?type=both&market=BTC-LTC
    final_url = BITTREX_GET_ORDER_BOOK + pair_name

    if should_print_debug():
        print final_url

    return final_url


def get_order_book_bittrex(pair_name, timest):

    final_url = get_order_book_bittrex_url(pair_name, timest)

    err_msg = "get_order_book_bittrex called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        return OrderBook.from_bittrex(r["result"], pair_name, timest)

    return None


def get_order_book_bittrex_result_processor(json_document, pair_name, timest):

    if json_document is not None and "result" in json_document:
        return OrderBook.from_bittrex(json_document["result"], pair_name, timest)

    return None