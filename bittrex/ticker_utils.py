from bittrex.constants import BITTREX_GET_TICKER
from bittrex.error_handling import is_error

from data.Ticker import Ticker

from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, LOG_ALL_ERRORS, ERROR_LOG_FILE_NAME

from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_ticker_bittrex_url(pair_name, timest):
    # https://bittrex.com/api/v1.1/public/getticker?market=BTC-LTC
    final_url = BITTREX_GET_TICKER + pair_name

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_ticker_bittrex(pair_name, timest):

    final_url = get_ticker_bittrex_url(pair_name, timest)

    err_msg = "get_ticker_bittrex called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        return get_ticker_bittrex_result_processor(json_document, pair_name, timest)

    return None


def get_ticker_bittrex_result_processor(json_document, pair_name, timest):
    if is_error(json_document):

        msg = "get_ticker_bittrex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    return Ticker.from_bittrex(pair_name, timest, json_document["result"])
