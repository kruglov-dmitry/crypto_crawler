from constants import KRAKEN_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request


def get_ticker_kraken(currency, timest):
    # https://api.kraken.com/0/public/Ticker?pair=DASHXBT
    final_url = KRAKEN_GET_TICKER + currency

    if should_print_debug():
        print final_url

    err_msg = "get_ticker_kraken called for {pair} at {timest}".format(pair=currency, timest=timest)
    r = send_request(final_url, err_msg)

    if r is not None and "result" in r:
        if currency in r["result"]:
            return Ticker.from_kraken(currency, timest, r["result"][currency])

    return None
