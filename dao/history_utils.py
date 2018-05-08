from binance.constants import BINANCE_CURRENCY_PAIRS
from binance.history_utils import get_history_binance, get_history_binance_url, get_history_binance_result_processor
from bittrex.constants import BITTREX_CURRENCY_PAIRS
from bittrex.history_utils import get_history_bittrex, get_history_bittrex_url, get_history_bittrex_result_processor
from constants import HTTP_TIMEOUT_SECONDS
from data_access.classes.WorkUnit import WorkUnit
from enums.currency_pair import CURRENCY_PAIR
from enums.exchange import EXCHANGE
from kraken.constants import KRAKEN_CURRENCY_PAIRS
from kraken.history_utils import get_history_kraken, get_history_kraken_url, get_history_kraken_result_processor
from poloniex.constants import POLONIEX_CURRENCY_PAIRS
from poloniex.history_utils import get_history_poloniex, get_history_poloniex_url, get_history_poloniex_result_processor
from utils.currency_utils import get_currency_pair_name_by_exchange_id
from huobi.constants import HUOBI_CURRENCY_PAIRS
from huobi.history_utils import get_history_huobi, get_history_huobi_result_processor, get_history_huobi_url


def get_history_speedup(date_start, date_end, processor):

    history_async_requests = []

    for exchange_id in EXCHANGE.values():
	if exchange_id != EXCHANGE.KRAKEN:
		continue
        for pair_id in CURRENCY_PAIR.values():

            pair_name = get_currency_pair_name_by_exchange_id(pair_id, exchange_id)
            if pair_name is None:
                continue

            method_for_url = get_history_url_by_exchange_id(exchange_id)
            request_url = method_for_url(pair_name, date_start, date_end)
            constructor = get_history_constructor_by_exchange_id(exchange_id)

            history_async_requests.append(WorkUnit(request_url, constructor, pair_name, date_end))

    return processor.process_async(history_async_requests, HTTP_TIMEOUT_SECONDS)


def get_history_url_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_history_bittrex_url,
        EXCHANGE.KRAKEN: get_history_kraken_url,
        EXCHANGE.POLONIEX: get_history_poloniex_url,
        EXCHANGE.BINANCE: get_history_binance_url,
        EXCHANGE.HUOBI: get_history_huobi_url
    }[exchange_id]


def get_history(prev_time, now_time):
    all_history = []

    for currency in POLONIEX_CURRENCY_PAIRS:
        all_history += get_history_poloniex(currency, prev_time, now_time)

    for currency in KRAKEN_CURRENCY_PAIRS:
        all_history += get_history_kraken(currency, prev_time, now_time)

    for currency in BITTREX_CURRENCY_PAIRS:
        all_history += get_history_bittrex(currency, prev_time, now_time)

    for currency in BINANCE_CURRENCY_PAIRS:
        all_history += get_history_binance(currency, prev_time, now_time)

    for currency in HUOBI_CURRENCY_PAIRS:
        all_history += get_history_huobi(currency, prev_time, now_time)

    return all_history


def get_history_constructor_by_exchange_id(exchange_id):
    """
        Return functor that expect following arguments:
            json_array,
            exchange specific name of currency
            date_start
            date_end
        It will return array of object from data/* folder
    """
    return {
        EXCHANGE.BITTREX: get_history_bittrex_result_processor,
        EXCHANGE.KRAKEN: get_history_kraken_result_processor,
        EXCHANGE.POLONIEX: get_history_poloniex_result_processor,
        EXCHANGE.BINANCE: get_history_binance_result_processor,
        EXCHANGE.HUOBI: get_history_huobi_result_processor,
    }[exchange_id]
