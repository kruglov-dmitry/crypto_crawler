from huobi.constants import HUOBI_GET_TICKER
from huobi.error_handling import is_error

from data.ticker import Ticker

from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, LOG_ALL_ERRORS, ERROR_LOG_FILE_NAME

from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_ticker_huobi_url(pair_name, timest):
    final_url = HUOBI_GET_TICKER + pair_name

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_ticker_huobi(pair_name, timest):

    final_url = get_ticker_huobi_url(pair_name, timest)

    err_msg = "get_ticker_huobi called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        return get_ticker_huobi_result_processor(json_document, pair_name, timest)

    return None


def get_ticker_huobi_result_processor(json_document, pair_name, timest):
    if is_error(json_document) or json_document["tick"] is None:

        msg = "get_ticker_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    return Ticker.from_huobi(pair_name, timest, json_document["tick"])
