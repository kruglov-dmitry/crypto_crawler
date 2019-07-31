from kraken.constants import KRAKEN_GET_TICKER
from kraken.error_handling import is_error

from data.ticker import Ticker

from data_access.internet import send_request

from enums.status import STATUS

from debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file


def get_ticker_kraken_url(pair_name, timest):
    # https://api.kraken.com/0/public/Ticker?pair=DASHXBT
    final_url = KRAKEN_GET_TICKER + pair_name

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_ticker_kraken(pair_name, timest):

    final_url = get_ticker_kraken_url(pair_name, timest)

    err_msg = "get_ticker_kraken called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        get_ticker_kraken_result_processor(json_document, pair_name, timest)

    return error_code, json_document


def get_ticker_kraken_result_processor(json_document, pair_name, timest):

    if is_error(json_document):

        msg = "get_order_book_kraken_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    if pair_name in json_document["result"]:
        return Ticker.from_kraken(pair_name, timest, json_document["result"][pair_name])

    return None
