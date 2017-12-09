from constants import KRAKEN_GET_HISTORY
from data.OrderHistory import OrderHistory
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_history_kraken_url(currency, prev_time, now_time):
    all_history_records = []

    # https://api.kraken.com/0/public/Trades?pair=XETHXXBT&since=1501693512
    # FIXME should be id !
    final_url = KRAKEN_GET_HISTORY + currency # + "&since=" + str(prev_time)

    if should_print_debug():
        print final_url

    return final_url


def get_history_kraken(currency, prev_time, now_time):
    all_history_records = []

    final_url = get_history_kraken_url(currency, prev_time, now_time)

    err_msg = "get_history_kraken called for {pair} at {timest}".format(pair=currency, timest=now_time)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        if currency in r["result"]:
            for rr in r["result"][currency]:
                all_history_records.append(OrderHistory.from_kraken(rr, currency, now_time))

    return all_history_records
