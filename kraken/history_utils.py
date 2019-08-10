from kraken.constants import KRAKEN_GET_HISTORY, EMPTY_LIST
from kraken.error_handling import is_error

from data.trade_history import TradeHistory

from utils.debug_utils import should_print_debug, print_to_console, ERROR_LOG_FILE_NAME, LOG_ALL_OTHER_STUFF
from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_history_kraken_url(pair_name, prev_time, now_time):
    """

    :param pair_name:
    :param prev_time:
    :param now_time: for backwards compatibility
    :return:
    """
    # https://api.kraken.com/0/public/Trades?pair=XETHXXBT&since=1501693512
    final_url = KRAKEN_GET_HISTORY + pair_name + "&since=" + str(prev_time)

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_history_kraken(pair_name, prev_time, now_time):

    final_url = get_history_kraken_url(pair_name, prev_time, now_time)

    err_msg = "get_history_kraken called for {pair} at {timest}".format(pair=pair_name, timest=now_time)
    status_code, json_document = send_request(final_url, err_msg)

    if status_code == STATUS.SUCCESS:
        return get_history_kraken_result_processor(json_document, pair_name, now_time)

    return EMPTY_LIST


def get_history_kraken_result_processor(json_document, pair_name, timest):
    all_history_records = EMPTY_LIST

    if is_error(json_document):

        msg = "get_history_kraken_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return all_history_records

    if pair_name in json_document["result"]:
        for rr in json_document["result"][pair_name]:
            all_history_records.append(TradeHistory.from_kraken(rr, pair_name, timest))

    return all_history_records
