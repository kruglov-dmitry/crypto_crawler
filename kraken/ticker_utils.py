from constants import KRAKEN_GET_TICKER
import requests
from data.Ticker import Ticker
from debug_utils import should_print_debug

HTTP_TIMEOUT_SECONDS = 5


def get_ticker_kraken(currency, timest):
    # https://api.kraken.com/0/public/Ticker?pair=DASHXBT
    final_url = KRAKEN_GET_TICKER + currency

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS).json()
        if "result" in r:
            return Ticker.from_kraken(currency, timest, r["result"][currency])
    except Exception, e:
        print "get_ticker_kraken: ", currency, timest, str(e)

    return None
