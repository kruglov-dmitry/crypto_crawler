from constants import BITTREX_GET_TICKER
import requests
from data.Ticker import Ticker
from debug_utils import should_print_debug

HTTP_TIMEOUT_SECONDS = 5


def get_ticker_bittrex(currency, timest):
    # https://bittrex.com/api/v1.1/public/getticker?market=BTC-LTC
    final_url = BITTREX_GET_TICKER + currency

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS).json()
        if "result" in r:
            return Ticker.from_bittrex(currency, timest, r["result"])
    except Exception, e:
        print "get_ticker_bittrex: ", currency, timest, str(e)

    return None
