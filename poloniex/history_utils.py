from poloniex.constants import POLONIEX_GET_HISTORY

from data.OrderHistory import OrderHistory

from debug_utils import should_print_debug

from data_access.internet import send_request

from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF
from enums.status import STATUS


def get_history_poloniex_url(pair_name, prev_time, now_time):
    # https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1501693512&end=1501693572
    final_url = POLONIEX_GET_HISTORY + pair_name + "&start=" + str(prev_time) + "&end=" + str(now_time)

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_history_poloniex(pair_name, prev_time, now_time):
    all_history_records = []

    final_url = get_history_poloniex_url(pair_name, prev_time, now_time)

    err_msg = "get_history_poloniex called for {pair} at {timest}".format(pair=pair_name, timest=now_time)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None:
        for rr in r:
            all_history_records.append(OrderHistory.from_poloniex(rr, pair_name, now_time))

    return all_history_records


def get_history_poloniex_result_processor(json_document, pair_name, timest):
    all_history_records = []

    if json_document is not None:
        for rr in json_document:
            all_history_records.append(OrderHistory.from_poloniex(rr, pair_name, timest))

    return all_history_records