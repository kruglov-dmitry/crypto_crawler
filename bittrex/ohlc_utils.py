from constants import BITTREX_GET_OHLC
from data.Candle import Candle
from debug_utils import should_print_debug
from data_access.internet import send_request


def get_ohlc_bittrex(currency, date_end, date_start, period):
    result_set = []
    # https://bittrex.com/Api/v2.0/pub/market/GetTicks?tickInterval=oneMin&marketName=BTC-ETH&_=timest

    final_url = BITTREX_GET_OHLC + period + "&marketName=" + currency + "&_=" + str(date_start)

    if should_print_debug():
        print final_url

    err_msg = "get_ohlc_bittrex called for {pair} at {timest}".format(pair=currency, timest=date_start)
    r = send_request(final_url, err_msg)

    if r is not None and "result" in r:
        # result":[{"O":0.08184725,"H":0.08184725,"L":0.08181559,"C":0.08181559,"V":9.56201864,"T":"2017-07-21T17:26:00","BV":0.78232812},
        # {"O":0.08181559,"H":0.08184725,"L":0.08181559,"C":0.08184725,"V":3.28483907,"T":"2017-07-21T17:27:00","BV":0.26876032}
        for record in r["result"]:
            result_set.append(Candle.from_bittrex(record, currency))

    return result_set
