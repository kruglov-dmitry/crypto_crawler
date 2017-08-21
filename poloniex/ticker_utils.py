from constants import POLONIEX_GET_TICKER
import requests
from data.Ticker import Ticker
from debug_utils import should_print_debug

HTTP_TIMEOUT_SECONDS = 5


def get_ticker_poloniex(currency, timest):
    final_url = POLONIEX_GET_TICKER

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS)
        return Ticker.from_poloniex(currency, timest, r.json()[currency])
    except Exception, e:
        print "get_ticker_poloniex: ", currency, timest, str(e)

    return None
