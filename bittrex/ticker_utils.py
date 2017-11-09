from constants import BITTREX_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request


def get_ticker_bittrex(currency, timest):
    # https://bittrex.com/api/v1.1/public/getticker?market=BTC-LTC
    final_url = BITTREX_GET_TICKER + currency

    if should_print_debug():
        print final_url

    err_msg = "get_ticker_bittrex called for {pair} at {timest}".format(pair=currency, timest=timest)
    r = send_request(final_url, err_msg)

    if r is not None and "result" in r and r["result"] is not None:
        try:
            return Ticker.from_bittrex(currency, timest, r["result"])
        except Exception, e:
            print "Error get ticket bitrex", str(e), "for data"
            print r["result"]

    return None
