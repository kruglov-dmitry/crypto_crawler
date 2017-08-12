from constants import KRAKEN_GET_HISTORY
import requests
from data.OrderHistory import OrderHistory
from daemon import should_print_debug


def get_history_kraken(currency, prev_time, now_time):
    all_history_records = []

    # https://api.kraken.com/0/public/Trades?pair=XETHXXBT&since=1501693512
    # FIXME should be id !
    final_url = KRAKEN_GET_HISTORY + currency # + "&since=" + str(prev_time)

    if should_print_debug():
        print final_url

    try:
        r = requests.get(final_url).json()

        if "result" in r:
            for rr in r["result"][currency]:
                all_history_records.append(OrderHistory.from_kraken(rr, currency, now_time))
    except Exception, e:
        print "get_history_kraken: ", currency, now_time, str(e)

    return all_history_records
