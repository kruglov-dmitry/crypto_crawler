from constants import BINANCE_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS
from utils.currency_utils import get_currency_pair_from_binance


def get_tickers_binance(currency_names, timest):

    """
   {"symbol":"ETHBTC","bidPrice":"0.04039700","bidQty":"4.50700000","askPrice":"0.04047500","askQty":"1.30600000"},
   {"symbol":"LTCBTC","bidPrice":"0.00875700","bidQty":"0.24000000","askPrice":"0.00876200","askQty":"0.01000000"},

    :param currency_names:
    :param timest:
    :return:
    """
    final_url = BINANCE_GET_TICKER

    if should_print_debug():
        print final_url

    err_msg = "get_tickers_binance called for list of pairS at {timest}".format(timest=timest)
    error_code, r = send_request(final_url, err_msg)

    res = {}
    if error_code == STATUS.SUCCESS and r is not None:
        for entry in r:
            if entry["symbol"] in currency_names:
                pair_id = get_currency_pair_from_binance(entry["symbol"])
                res[pair_id] = Ticker.from_binance(entry["symbol"], timest, entry)

    return res