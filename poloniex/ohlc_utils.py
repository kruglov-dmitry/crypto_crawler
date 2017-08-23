from constants import POLONIEX_GET_OHLC
from data.Candle import Candle
from debug_utils import should_print_debug
from data_access.internet import send_request


def get_ohlc_poloniex(currency, date_end, date_start, period):
    result_set = []
    final_url = POLONIEX_GET_OHLC + currency + "&start=" + str(date_start) + \
                "&end=" + str(date_end) + "&period=" + str(period)

    if should_print_debug():
        print final_url

    err_msg = "get_ohlc_poloniex called for {pair} at {timest}".format(pair=currency, timest=date_start)
    r = send_request(final_url, err_msg)

    if r is not None:
        for record in r:
            result_set.append(Candle.from_poloniex(record, currency))

    return result_set
