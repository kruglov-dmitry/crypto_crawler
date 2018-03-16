from binance.constants import BINANCE_GET_HISTORY, EMPTY_LIST
from binance.error_handling import is_error

from data.TradeHistory import TradeHistory

from debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_history_binance_url(pair_name, date_start, date_end):
    # https://api.binance.com/api/v1/aggTrades?symbol=XMRETH
    # Optional startTime, endTime
    final_url = BINANCE_GET_HISTORY + pair_name

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_history_binance(pair_name, prev_time, now_time):

    final_url = get_history_binance_url(pair_name, prev_time, now_time)

    err_msg = "get_history_binance called for {pair} at {timest}".format(pair=pair_name, timest=prev_time)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        return get_history_binance_result_processor(json_document, pair_name, now_time)

    return EMPTY_LIST


def get_history_binance_result_processor(json_document, pair_name, timest):
    """
          {
            "a": 26129,         // Aggregate tradeId
            "p": "0.01633102",  // Price
            "q": "4.70443515",  // Quantity
            "f": 27781,         // First tradeId
            "l": 27781,         // Last tradeId
            "T": 1498793709153, // Timestamp
            "m": true,          // Was the buyer the maker?
            "M": true           // Was the trade the best price match?
          }
    """

    all_history_records = []

    if is_error(json_document):

        msg = "get_history_binance_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return all_history_records

    for record in json_document:
        all_history_records.append(TradeHistory.from_binance(record, pair_name, timest))

    return all_history_records