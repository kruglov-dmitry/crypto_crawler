from constants import POLONIEX_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request


def get_ticker_poloniex(currency, timest):
    final_url = POLONIEX_GET_TICKER

    if should_print_debug():
        print final_url

    err_msg = "get_ticker_poloniex called for {pair} at {timest}".format(pair=currency, timest=timest)
    r = send_request(final_url, err_msg)

    if r is not None and currency in r:
        return Ticker.from_poloniex(currency, timest, r[currency])

    return None
