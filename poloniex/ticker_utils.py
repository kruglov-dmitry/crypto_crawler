from constants import POLONIEX_GET_TICKER
import requests
from data.Ticker import Ticker
from daemon import should_print_debug


def get_ticker_poloniex(currency, timest):
    final_url = POLONIEX_GET_TICKER

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url)
        return Ticker.from_poloniex(currency, timest, r.json()[currency])
    except Exception, e:
        print "get_ticker_poloniex: ", currency, timest, str(e)

    return None