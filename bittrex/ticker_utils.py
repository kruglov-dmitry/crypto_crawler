from constants import BITTREX_GET_TICKER
from data.Ticker import Ticker
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_ticker_bittrex_url(pair_name, timest):
    # https://bittrex.com/api/v1.1/public/getticker?market=BTC-LTC
    final_url = BITTREX_GET_TICKER + pair_name

    if should_print_debug():
        print final_url

    return final_url


def get_ticker_bittrex(pair_name, timest):

    final_url = get_ticker_bittrex_url(pair_name, timest)

    err_msg = "get_ticker_bittrex called for {pair} at {timest}".format(pair=pair_name, timest=timest)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r and r["result"] is not None:
        try:
            return Ticker.from_bittrex(pair_name, timest, r["result"])
        except Exception, e:
            print "Error get ticket bitrex", str(e), "for data"
            print r["result"]

    return None


def get_ticker_bittrex_result_processor(json_document, pair_name, timest):
    if json_document is not None and "result" in json_document and json_document["result"] is not None:
        try:
            return Ticker.from_bittrex(pair_name, timest, json_document["result"])
        except Exception, e:
            print "Error get ticket bitrex", str(e), "for data"
            print json_document["result"]

    return None