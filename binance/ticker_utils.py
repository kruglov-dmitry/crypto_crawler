from binance.constants import BINANCE_GET_TICKER
from binance.error_handling import is_error

from data.ticker import Ticker

from utils.debug_utils import should_print_debug, print_to_console, LOG_ALL_OTHER_STUFF, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_tickers_binance_url(pair_name):
    final_url = BINANCE_GET_TICKER

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_OTHER_STUFF)

    return final_url


def get_tickers_binance(pair_name, timest):

    """
   {"symbol":"ETHBTC","bidPrice":"0.04039700","bidQty":"4.50700000","askPrice":"0.04047500","askQty":"1.30600000"},
   {"symbol":"LTCBTC","bidPrice":"0.00875700","bidQty":"0.24000000","askPrice":"0.00876200","askQty":"0.01000000"},

    :param pair_name:
    :param timest:
    :return:
    """

    final_url = get_tickers_binance_url(pair_name)

    err_msg = "get_tickers_binance called for list of pairS at {timest}".format(timest=timest)
    error_code, r = send_request(final_url, err_msg)

    res = []
    if error_code == STATUS.SUCCESS and r is not None:
        for entry in r:
            if entry["symbol"] in pair_name:
                res.append(Ticker.from_binance(entry["symbol"], timest, entry))

    return res


def get_ticker_binance(pair_name, timest):
    final_url = get_tickers_binance_url(pair_name)

    err_msg = "get_ticker_binance called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, json_document = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        return get_ticker_binance_result_processor(json_document, pair_name, timest)

    return None


def get_ticker_binance_result_processor(json_document, pair_name, timest):

    if is_error(json_document):

        msg = "get_ticker_binance_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    for entry in json_document:
        if pair_name in entry["symbol"]:
            return Ticker.from_binance(entry["symbol"], timest, entry)

    return None
