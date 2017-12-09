from constants import BITTREX_GET_OHLC
from data.Candle import Candle
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS
from utils.file_utils import log_to_file


def get_ohlc_bittrex_url(currency, date_start, date_end, period):
    result_set = []
    # https://bittrex.com/Api/v2.0/pub/market/GetTicks?tickInterval=oneMin&marketName=BTC-ETH&_=timest

    final_url = BITTREX_GET_OHLC + period + "&marketName=" + currency + "&_=" + str(date_start)

    if should_print_debug():
        print final_url

    return final_url


def get_ohlc_bittrex_result_processor(json_responce, currency, date_start, date_end):
    result_set = []

    log_to_file(json_responce, "bittrex_ohlc.txt")

    if json_responce is not None and "result" in json_responce:
        # result":[{"O":0.08184725,"H":0.08184725,"L":0.08181559,"C":0.08181559,"V":9.56201864,"T":"2017-07-21T17:26:00","BV":0.78232812},
        # {"O":0.08181559,"H":0.08184725,"L":0.08181559,"C":0.08184725,"V":3.28483907,"T":"2017-07-21T17:27:00","BV":0.26876032}
        if json_responce["result"] is not None:
            for record in json_responce["result"]:
                new_candle = Candle.from_bittrex(record, currency)
                if new_candle.timest >= date_start:  # NOTE: API V2 tend to ignore time parameter - so we have to filter it manually
                    result_set.append(new_candle)

    return result_set

def get_ohlc_bittrex(currency, date_start, date_end, period):
    result_set = []

    final_url = get_ohlc_bittrex_url(currency, date_start, date_end, period)

    err_msg = "get_ohlc_bittrex called for {pair} at {timest}".format(pair=currency, timest=date_start)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None and "result" in r:
        # result":[{"O":0.08184725,"H":0.08184725,"L":0.08181559,"C":0.08181559,"V":9.56201864,"T":"2017-07-21T17:26:00","BV":0.78232812},
        # {"O":0.08181559,"H":0.08184725,"L":0.08181559,"C":0.08184725,"V":3.28483907,"T":"2017-07-21T17:27:00","BV":0.26876032}
        if r["result"] is not None:
            for record in r["result"]:
                new_candle = Candle.from_bittrex(record, currency)
                # if new_candle.timest >= date_end:   # NOTE: API V2 tend to ignore time parameter - so we have to filter it manually
                result_set.append(new_candle)

    return result_set
