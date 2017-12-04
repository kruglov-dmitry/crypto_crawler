from constants import BITTREX_GET_HISTORY
from data.OrderHistory import OrderHistory
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_history_binance(currency, prev_time, now_time):
    all_history_records = []

    if should_print_debug():
        print "get_history_binance: NOT IMPLEMENTED!"

    return all_history_records
