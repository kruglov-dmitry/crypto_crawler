from poloniex.constants import POLONIEX_GET_OHLC

from data.Candle import Candle

from data_access.internet import send_request

from enums.status import STATUS

from debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG


def get_ohlc_poloniex_url(currency, date_start, date_end, period):

    final_url = POLONIEX_GET_OHLC + currency + "&start=" + str(date_start) + \
                "&end=" + str(date_end) + "&period=" + str(period)

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_ohlc_poloniex_result_processor(json_responce, currency, date_start, date_end):
    result_set = []

    if json_responce is not None:
        for record in json_responce:
            result_set.append(Candle.from_poloniex(record, currency))

    return result_set


def get_ohlc_poloniex(currency, date_start, date_end, period):
    result_set = []

    final_url = get_ohlc_poloniex_url(currency, date_start, date_end, period)

    err_msg = "get_ohlc_poloniex called for {pair} at {timest}".format(pair=currency, timest=date_start)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None:
        for record in r:
            result_set.append(Candle.from_poloniex(record, currency))

    return result_set
