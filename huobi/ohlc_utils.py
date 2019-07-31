# coding=utf-8
from huobi.constants import HUOBI_GET_OHLC
from huobi.error_handling import is_error

from data.candle import Candle

from debug_utils import should_print_debug, print_to_console, LOG_ALL_DEBUG, ERROR_LOG_FILE_NAME
from utils.file_utils import log_to_file

from data_access.internet import send_request

from enums.status import STATUS


def get_ohlc_huobi_url(pair_name, date_start, date_end, period):
    date_start_ms = 1000 * date_start
    # market/history/kline?period=1day&size=200&symbol=btcusdt
    final_url = HUOBI_GET_OHLC + pair_name + "&period=" + period

    if should_print_debug():
        print_to_console(final_url, LOG_ALL_DEBUG)

    return final_url


def get_ohlc_huobi_result_processor(json_response, pair_name, date_start, date_end):
    """
        {
          "status": "ok",
          "ch": "market.btcusdt.kline.1day",
          "ts": 1499223904680,
          “data”: [
            {
                "id": 1499184000,
                "amount": 37593.0266,
                "count": 0,
                "open": 1935.2000,
                "close": 1879.0000,
                "low": 1856.0000,
                "high": 1940.0000,
                "vol": 71031537.97866500
            },
            // more data here
            ]
        }
    """
    result_set = []

    if is_error(json_response) and "data" not in json_response:

        msg = "get_ohlc_huobi_result_processor - error response - {er}".format(er=json_response)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return result_set

    for record in json_response["data"]:
        record["artifical_ts"] = json_response["ts"]
        result_set.append(Candle.from_huobi(record, pair_name))

    return result_set


def get_ohlc_huobi(currency, date_start, date_end, period):
    result_set = []

    final_url = get_ohlc_huobi_url(currency, date_start, date_end, period)

    err_msg = "get_ohlc_huobi called for {pair} at {timest}".format(pair=currency, timest=date_start)
    error_code, json_responce = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS:
        result_set = get_ohlc_huobi_result_processor(json_responce, currency, date_start, date_end)

    return result_set
