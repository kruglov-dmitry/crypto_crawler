from constants import KRAKEN_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_ticker_kraken_url(currency, timest):
    # https://api.kraken.com/0/public/Ticker?pair=DASHXBT
    final_url = KRAKEN_GET_TICKER + currency

    if should_print_debug():
        print final_url

    return final_url


def get_ticker_kraken(currency, timest):

    final_url = get_ticker_kraken(currency, timest)

    err_msg = "get_ticker_kraken called for {pair} at {timest}".format(pair=currency, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        if currency in r["result"]:
            return Ticker.from_kraken(currency, timest, r["result"][currency])

    return None


def get_ticker_kraken_result_processor(json_document, pair_name, timest):
    if json_document is not None and "result" in json_document:
        if pair_name in json_document["result"]:
            return Ticker.from_kraken(pair_name, timest, json_document["result"][pair_name])

    return None