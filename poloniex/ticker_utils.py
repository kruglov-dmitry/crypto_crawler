from constants import POLONIEX_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS
from currency_utils import get_currency_pair_from_poloniex


def get_ticker_poloniex_url(currency_names, timest):
    final_url = POLONIEX_GET_TICKER

    if should_print_debug():
        print final_url

    return final_url


def get_tickers_poloniex(currency_names, timest):
    final_url = get_ticker_poloniex_url(currency_names, timest)

    err_msg = "get_ticker_poloniex called for list of pairS at {timest}".format(timest=timest)
    error_code, r = send_request(final_url, err_msg)

    res = {}
    if error_code == STATUS.SUCCESS and r is not None:
        for pair_name in currency_names:
            if pair_name in r and r[pair_name] is not None:
                pair_id = get_currency_pair_from_poloniex(pair_name)
                res[pair_id] = Ticker.from_poloniex(pair_name, timest, r[pair_name])

    return res