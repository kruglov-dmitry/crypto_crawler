from constants import POLONIEX_GET_OHLC
import requests
from data.Candle import Candle
from debug_utils import should_print_debug


def get_ohlc_poloniex(currency, date_end, date_start, period):
    result_set = []
    final_url = POLONIEX_GET_OHLC + currency + "&start=" + str(date_start) + \
                "&end=" + str(date_end) + "&period=" + str(period)

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        for record in r:
            result_set.append(Candle.from_poloniex(record, currency))
    except Exception, e:
        print "get_ohlc_poloniex: ", currency, date_start, str(e)

    return result_set
