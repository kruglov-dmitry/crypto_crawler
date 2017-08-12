from constants import BITTREX_GET_HISTORY
import requests
from data.OrderHistory import OrderHistory
from daemon import should_print_debug


def get_history_bittrex(currency, prev_time, now_time):
    all_history_records = []

    # https://bittrex.com/api/v1.1/public/getmarkethistory?market=BTC-LTC
    final_url = BITTREX_GET_HISTORY + currency + "&since=" + str(prev_time)

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        if "result" in r:
            for rr in r["result"]:
                all_history_records.append(OrderHistory.from_bittrex(rr, currency, now_time))
    except Exception, e:
        print "get_history_bittrex: ", currency, now_time, str(e)

    return all_history_records
