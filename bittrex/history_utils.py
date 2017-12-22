from constants import BITTREX_GET_HISTORY
from data.OrderHistory import OrderHistory
from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF
from data_access.internet import send_request
from enums.status import STATUS


def get_history_bittrex_url(pair_name, prev_time, now_time):
    # https://bittrex.com/api/v1.1/public/getmarkethistory?market=BTC-LTC
    final_url = BITTREX_GET_HISTORY + pair_name + "&since=" + str(prev_time)

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_history_bittrex(pair_name, prev_time, now_time):
    all_history_records = []

    final_url = get_history_bittrex_url(pair_name, prev_time, now_time)

    err_msg = "get_history_bittrex called for {pair} at {timest}".format(pair=pair_name, timest=now_time)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        for rr in r["result"]:
            all_history_records.append(OrderHistory.from_bittrex(rr, pair_name, now_time))

    return all_history_records


def get_history_bittrex_result_processor(json_document, pair_name, timest):
    all_history_records = []

    if json_document is not None and "result" in json_document and json_document["result"] is not None:
        for rr in json_document["result"]:
            all_history_records.append(OrderHistory.from_bittrex(rr, pair_name, timest))

    return all_history_records
