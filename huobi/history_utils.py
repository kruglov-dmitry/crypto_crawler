from huobi.constants import HUOBI_GET_HISTORY, EMPTY_LIST
from huobi.error_handling import is_error

from data.TradeHistory import TradeHistory

from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_history_huobi_url(pair_name, date_start, date_end):

    final_url = HUOBI_GET_HISTORY + pair_name

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_history_huobi(pair_name, prev_time, now_time):

    final_url = get_history_huobi_url(pair_name, prev_time, now_time)

    err_msg = "get_history_huobi called for {pair} at {timest}".format(pair=pair_name, timest=prev_time)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        return get_history_huobi_result_processor(json_document, pair_name, now_time)

    return EMPTY_LIST


def get_history_huobi_result_processor(json_document, pair_name, timest):
    all_history_records = []

    if is_error(json_document) or "data" not in json_document or "data" not in json_document["data"]:

        msg = "get_history_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return all_history_records

    for record in json_document["data"]["data"]:
        all_history_records.append(TradeHistory.from_huobi(record, pair_name, timest))

    return all_history_records