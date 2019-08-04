from kraken.constants import KRAKEN_GET_ORDER_BOOK
from kraken.error_handling import is_error

from data.order_book import OrderBook

from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS

from debug_utils import print_to_console, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME, should_print_debug


def get_order_book_kraken_url(pair_name):
    # https://api.kraken.com/0/public/Depth?pair=XETHXXBT
    final_url = KRAKEN_GET_ORDER_BOOK + pair_name

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_order_book_kraken(pair_name, timest):

    final_url = get_order_book_kraken_url(pair_name)

    err_msg = "get_order_book_kraken called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        return get_order_book_kraken_result_processor(json_document, pair_name, timest)

    return None


def get_order_book_kraken_result_processor(json_document, pair_name, timest):

    if is_error(json_document):

        msg = "get_order_book_kraken_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    if pair_name in json_document["result"]:
        return OrderBook.from_kraken(json_document["result"][pair_name], pair_name, timest)

    return None
