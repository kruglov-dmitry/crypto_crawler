from constants import BITTREX_GET_HISTORY
from data.OrderHistory import OrderHistory
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_history_bittrex(currency, prev_time, now_time):
    all_history_records = []

    # https://bittrex.com/api/v1.1/public/getmarkethistory?market=BTC-LTC
    final_url = BITTREX_GET_HISTORY + currency + "&since=" + str(prev_time)

    if should_print_debug():
        print final_url

    err_msg = "get_history_bittrex called for {pair} at {timest}".format(pair=currency, timest=now_time)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        for rr in r["result"]:
            all_history_records.append(OrderHistory.from_bittrex(rr, currency, now_time))

    return all_history_records
