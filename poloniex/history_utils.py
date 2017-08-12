from constants import POLONIEX_GET_HISTORY
import requests
from data.OrderHistory import OrderHistory
from daemon import should_print_debug

def get_history_poloniex(currency, prev_time, now_time):
    all_history_records = []

    # https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1501693512&end=1501693572
    final_url =  POLONIEX_GET_HISTORY + currency + "&start=" + str(prev_time) + "&end=" + str(now_time)

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        for rr in r:
            all_history_records.append(OrderHistory.from_poloniex(rr, currency, now_time))
    except Exception, e:
        print "get_history_poloniex: ", currency, now_time, str(e)

    return all_history_records
