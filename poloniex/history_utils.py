from poloniex.constants import POLONIEX_GET_HISTORY
from poloniex.error_handling import is_error

from data.trade_history import TradeHistory

from data_access.internet import send_request

from utils.debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file
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
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        all_history_records = get_history_poloniex_result_processor(json_document, pair_name, now_time)

    return all_history_records


def get_history_poloniex_result_processor(json_document, pair_name, timest):
    all_history_records = []

    if is_error(json_document):

        msg = "get_history_poloniex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return all_history_records

    for rr in json_document:
        all_history_records.append(TradeHistory.from_poloniex(rr, pair_name, timest))

    return all_history_records
