from constants import POLONIEX_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG
from data_access.internet import send_request
from enums.status import STATUS
from currency_utils import get_currency_pair_from_poloniex


def get_ticker_poloniex_url(currency_names, timest):
    final_url = POLONIEX_GET_TICKER

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_tickers_poloniex(currency_names, timest):
    final_url = get_ticker_poloniex_url(currency_names, timest)

    err_msg = "get_tickerS_poloniex called for list of pairS at {timest}".format(timest=timest)
    error_code, r = send_request(final_url, err_msg)

    res = []
    if error_code == STATUS.SUCCESS and r is not None:
        for pair_name in currency_names:
            if pair_name in r and r[pair_name] is not None:
                res.append(Ticker.from_poloniex(pair_name, timest, r[pair_name]))

    return res


def get_ticker_poloniex(pair_name, timest):
    final_url = get_ticker_poloniex_url(pair_name, timest)

    err_msg = "get_ticker_poloniex called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, json_response = send_request(final_url, err_msg)

    res = None
    if error_code == STATUS.SUCCESS and json_response is not None and pair_name in json_response and \
                    json_response[pair_name] is not None:
        res = Ticker.from_poloniex(pair_name, timest, json_response[pair_name])

    return res


def get_ticker_poloniex_result_processor(json_document, pair_name, timest):
    if json_document is not None and pair_name in json_document and json_document[pair_name] is not None:
        return Ticker.from_poloniex(pair_name, timest, json_document[pair_name])

    return None
