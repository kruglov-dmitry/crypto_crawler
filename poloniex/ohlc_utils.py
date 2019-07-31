from poloniex.constants import POLONIEX_GET_OHLC
from poloniex.error_handling import is_error

from data.candle import Candle

from data_access.internet import send_request

from enums.status import STATUS

from debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file


def get_ohlc_poloniex_url(currency, date_start, date_end, period):

    final_url = POLONIEX_GET_OHLC + currency + "&start=" + str(date_start) + \
                "&end=" + str(date_end) + "&period=" + str(period)

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_ohlc_poloniex_result_processor(json_response, pair_name, date_start, date_end):
    result_set = []

    if is_error(json_response):

        msg = "get_ohlc_poloniex_result_processor - error response - {er}".format(er=json_response)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return result_set

    for record in json_response:
        result_set.append(Candle.from_poloniex(record, pair_name))

    return result_set


def get_ohlc_poloniex(currency, date_start, date_end, period):
    result_set = []

    final_url = get_ohlc_poloniex_url(currency, date_start, date_end, period)

    err_msg = "get_ohlc_poloniex called for {pair} at {timest}".format(pair=currency, timest=date_start)
    error_code, json_responce = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        result_set = get_ohlc_poloniex_result_processor(json_responce, currency, date_start, date_end)

    return result_set
