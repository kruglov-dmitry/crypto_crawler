from constants import KRAKEN_GET_ORDER_BOOK
from data.OrderBook import OrderBook
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_order_book_kraken_url(pair_name, timest):
    # https://api.kraken.com/0/public/Depth?pair=XETHXXBT
    final_url = KRAKEN_GET_ORDER_BOOK + pair_name

    if should_print_debug():
        print final_url

    return final_url


def get_order_book_kraken(pair_name, timest):

    final_url = get_order_book_kraken_url(pair_name, timest)

    err_msg = "get_order_book_kraken called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        if pair_name in r["result"]:
            return OrderBook.from_kraken(r["result"][pair_name], pair_name, timest)

    return None


def get_order_book_kraken_result_processor(json_document, pair_name, timest):

    if json_document is not None and "result" in json_document:
        if pair_name in json_document["result"]:
            return OrderBook.from_kraken(json_document["result"][pair_name], pair_name, timest)

    return None