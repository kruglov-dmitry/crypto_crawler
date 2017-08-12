from constants import KRAKEN_GET_OHLC
import requests
from data.Candle import Candle
from daemon import should_print_debug

def get_ohlc_kraken(currency, date_end, date_start, period):
    result_set = []
    # https://api.kraken.com/0/public/OHLC?pair=XXRPXXBT&since=1501520850&interval=15
    final_url = KRAKEN_GET_OHLC + currency + "&since=" + str(date_start) + \
                "&interval=" + str(period)

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        if "result" in r:
            # "result":{"XXRPXXBT":[[1500873300,"0.00007037","0.00007055","0.00007012","0.00007053","0.00007035","104062.41283454",17],
            # [1500874200,"0.00007056","0.00007071","0.00007006","0.00007007","0.00007041","90031.72579746",33],
            for record in r["result"][currency]:
                result_set.append(Candle.from_kraken(record, currency))
    except Exception, e:
        print "get_ohlc_kraken: ", currency, date_start, str(e)

    return result_set
