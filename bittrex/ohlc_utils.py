from bittrex.constants import BITTREX_GET_OHLC
from bittrex.error_handling import is_error

from data.candle import Candle

from utils.debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_ohlc_bittrex_url(pair_name, date_start, date_end, period):
    result_set = []
    # https://bittrex.com/Api/v2.0/pub/market/GetTicks?tickInterval=oneMin&marketName=BTC-ETH&_=timest

    final_url = BITTREX_GET_OHLC + period + "&marketName=" + pair_name + "&_=" + str(date_start)

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_ohlc_bittrex_result_processor(json_document, pair_name, date_start, date_end):
    """
            result":[{"O":0.08184725,"H":0.08184725,"L":0.08181559,"C":0.08181559,"V":9.56201864,"T":"2017-07-21T17:26:00","BV":0.78232812},
            {"O":0.08181559,"H":0.08184725,"L":0.08181559,"C":0.08184725,"V":3.28483907,"T":"2017-07-21T17:27:00","BV":0.26876032}
    """

    result_set = []

    if is_error(json_document) or json_document["result"] is None:

        msg = "get_ohlc_bittrex_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return result_set

    for record in json_document["result"]:
        result_set.append(Candle.from_bittrex(record, pair_name))

    return result_set


def get_ohlc_bittrex(pair_name, date_start, date_end, period):
    result_set = []

    final_url = get_ohlc_bittrex_url(pair_name, date_start, date_end, period)

    err_msg = "get_ohlc_bittrex called for {pair} at {timest}".format(pair=pair_name, timest=date_start)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        result_set = get_ohlc_bittrex_result_processor(json_document, pair_name, date_start, date_end)

    return result_set
