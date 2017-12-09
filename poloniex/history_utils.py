from constants import POLONIEX_GET_HISTORY
from data.OrderHistory import OrderHistory
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_history_poloniex_url(currency, prev_time, now_time):
    all_history_records = []

    # https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1501693512&end=1501693572
    final_url =  POLONIEX_GET_HISTORY + currency + "&start=" + str(prev_time) + "&end=" + str(now_time)

    if should_print_debug():
        print final_url

    return final_url


def get_history_poloniex(currency, prev_time, now_time):
    all_history_records = []

    final_url = get_history_poloniex_url(currency, prev_time, now_time)

    err_msg = "get_history_poloniex called for {pair} at {timest}".format(pair=currency, timest=now_time)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None:
        for rr in r:
            all_history_records.append(OrderHistory.from_poloniex(rr, currency, now_time))

    return all_history_records
