from bittrex.constants import BITTREX_CURRENCY_PAIRS
from kraken.constants import KRAKEN_CURRENCY_PAIRS
from poloniex.constants import POLONIEX_CURRENCY_PAIRS
from binance.constants import BINANCE_CURRENCY_PAIRS

from bittrex.ohlc_utils import get_ohlc_bittrex, get_ohlc_bittrex_url, get_ohlc_bittrex_result_processor
from kraken.ohlc_utils import get_ohlc_kraken, get_ohlc_kraken_url, get_ohlc_kraken_result_processor
from poloniex.ohlc_utils import get_ohlc_poloniex, get_ohlc_poloniex_url, get_ohlc_poloniex_result_processor
from binance.ohlc_utils import get_ohlc_binance, get_ohlc_binance_url, get_ohlc_binance_result_processor

from enums.exchange import EXCHANGE
from enums.currency_pair import CURRENCY_PAIR

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from data_access.ConnectionPool import WorkUnit
from constants import HTTP_TIMEOUT_SECONDS


def get_candle_constructor_by_exchange_id(exchange_id):
    """
        Return functor that expect following arguments:
            json_array,
            exchange specific name of currency
            date_start
            date_end
        It will return array of object from data/* folder
    """
    return {
        EXCHANGE.BITTREX: get_ohlc_bittrex_result_processor,
        EXCHANGE.KRAKEN: get_ohlc_kraken_result_processor,
        EXCHANGE.POLONIEX: get_ohlc_poloniex_result_processor,
        EXCHANGE.BINANCE: get_ohlc_binance_result_processor
    }[exchange_id]


def get_ohlc_speedup(date_start, date_end, processor):

    ohlc_async_requests = []

    for exchange_id in EXCHANGE.values():
        for pair_id in CURRENCY_PAIR.values():

            pair_name = get_currency_pair_name_by_exchange_id(pair_id, exchange_id)
            if pair_name is None:
                continue

            period = get_ohlc_period_by_exchange_id(exchange_id)
            method_for_url = get_ohlc_url_by_echange_id(exchange_id)
            request_url = method_for_url(pair_name, date_start, date_end, period)
            construcotr = get_candle_constructor_by_exchange_id(exchange_id)

            ohlc_async_requests.append(WorkUnit(request_url, construcotr, pair_name, date_start, date_end))

    return processor.process_async(ohlc_async_requests, HTTP_TIMEOUT_SECONDS)


def get_ohlc(date_start, date_end):
    all_ohlc = []

    for currency in BITTREX_CURRENCY_PAIRS:
        period = "thirtyMin"
        all_ohlc += get_ohlc_bittrex(currency, date_start, date_end, period)

    for currency in KRAKEN_CURRENCY_PAIRS:
        period = 15
        all_ohlc += get_ohlc_kraken(currency, date_start, date_end, period)

    for currency in POLONIEX_CURRENCY_PAIRS:
        period = 14400
        all_ohlc += get_ohlc_poloniex(currency, date_start, date_end, period)

    for currency in BINANCE_CURRENCY_PAIRS:
        period = "15m"
        all_ohlc += get_ohlc_binance(currency, date_start, date_end, period)

    return all_ohlc


def get_ohlc_period_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: "thirtyMin",
        EXCHANGE.KRAKEN: 15,
        EXCHANGE.POLONIEX: 14400,
        EXCHANGE.BINANCE: "15m"
    }[exchange_id]


def get_ohlc_url_by_echange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_ohlc_bittrex_url,
        EXCHANGE.KRAKEN: get_ohlc_kraken_url,
        EXCHANGE.POLONIEX: get_ohlc_poloniex_url,
        EXCHANGE.BINANCE: get_ohlc_binance_url
    }[exchange_id]