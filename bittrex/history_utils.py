from bittrex.constants import BITTREX_GET_HISTORY
from bittrex.error_handling import is_error

from data.TradeHistory import TradeHistory

from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

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
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        all_history_records = get_history_bittrex_result_processor(json_document, pair_name, now_time)

    return all_history_records


def get_history_bittrex_result_processor(json_document, pair_name, timest):
    all_history_records = []

    if is_error(json_document) or json_document["result"] is None:

        msg = "get_history_bittrex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return all_history_records

    for rr in json_document["result"]:
        all_history_records.append(TradeHistory.from_bittrex(rr, pair_name, timest))

    return all_history_records
