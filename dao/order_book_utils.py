from bittrex.constants import BITTREX_CURRENCY_PAIRS
from kraken.constants import KRAKEN_CURRENCY_PAIRS
from poloniex.constants import POLONIEX_CURRENCY_PAIRS
from binance.constants import BINANCE_CURRENCY_PAIRS

from bittrex.order_book_utils import get_order_book_bittrex, get_order_book_bittrex_url, get_order_book_bittrex_result_processor
from kraken.order_book_utils import get_order_book_kraken, get_order_book_kraken_url, get_order_book_kraken_result_processor
from poloniex.order_book_utils import get_order_book_poloniex, get_order_book_poloniex_url, get_order_book_poloniex_result_processor
from binance.order_book_utils import get_order_book_binance, get_order_book_binance_url, get_order_book_binance_result_processor

from poloniex.currency_utils import get_currency_pair_to_poloniex
from bittrex.currency_utils import get_currency_pair_to_bittrex

from enums.exchange import EXCHANGE
from enums.currency_pair import CURRENCY_PAIR

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from data_access.ConnectionPool import WorkUnit

from collections import defaultdict

from utils.time_utils import get_now_seconds_local


def get_order_book_constructor_by_exchange_id(exchange_id):
    """
        Return functor that expect following arguments:
            json_array,
            exchange specific name of currency
            timest
        It will return array of object from data/* folder
    """
    return {
        EXCHANGE.BITTREX: get_order_book_bittrex_result_processor,
        EXCHANGE.KRAKEN: get_order_book_kraken_result_processor,
        EXCHANGE.POLONIEX: get_order_book_poloniex_result_processor,
        EXCHANGE.BINANCE: get_order_book_binance_result_processor
    }[exchange_id]


def get_order_book_speedup(date_start, date_end, processor):

    order_book_async_requests = []

    for exchange_id in EXCHANGE.values():
        for pair_id in CURRENCY_PAIR.values():

            pair_name = get_currency_pair_name_by_exchange_id(pair_id, exchange_id)
            if pair_name is None:
                continue

            method_for_url = get_order_book_url_by_echange_id(exchange_id)
            request_url = method_for_url(pair_name, date_start, date_end)
            constructor = get_order_book_constructor_by_exchange_id(exchange_id)

            order_book_async_requests.append(WorkUnit(request_url, constructor, pair_name, date_start, date_end))

    return processor.process_async(order_book_async_requests)


def get_order_book():

    all_order_book = defaultdict(list)

    timest = get_now_seconds_local()

    for currency in POLONIEX_CURRENCY_PAIRS:
        order_book = get_order_book_poloniex(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.POLONIEX].append(order_book)

    for currency in KRAKEN_CURRENCY_PAIRS:
        order_book = get_order_book_kraken(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.KRAKEN].append(order_book)

    for currency in BITTREX_CURRENCY_PAIRS:
        order_book = get_order_book_bittrex(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.BITTREX].append(order_book)

    for currency in BINANCE_CURRENCY_PAIRS:
        order_book = get_order_book_binance(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.BINANCE].append(order_book)

    return all_order_book


def get_order_book_by_pair(pair_id):
    """
        Used for arbitrage bot.

    :param pair_id:
    :return:
    """
    all_order_book = defaultdict(list)

    timest = get_now_seconds_local()

    poloniex_pair_name = get_currency_pair_to_poloniex(pair_id)
    order_book = get_order_book_poloniex(poloniex_pair_name, timest)
    if order_book is not None:
        all_order_book[EXCHANGE.POLONIEX].append(order_book)

    # kraken_pair_name = get_currency_pair_to_kraken(pair_id)
    # order_book = get_order_book_kraken(kraken_pair_name, timest)
    # if order_book is not None:
    #    all_order_book[EXCHANGE.KRAKEN].append(order_book)

    bittrex_pair_name = get_currency_pair_to_bittrex(pair_id)
    order_book = get_order_book_bittrex(bittrex_pair_name, timest)
    if order_book is not None:
        all_order_book[EXCHANGE.BITTREX].append(order_book)

    return all_order_book


def get_order_book_method_by_echange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_order_book_bittrex,
        EXCHANGE.KRAKEN: get_order_book_kraken,
        EXCHANGE.POLONIEX: get_order_book_poloniex,
        EXCHANGE.BINANCE: get_order_book_binance
    }[exchange_id]


def get_order_book_url_by_echange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_order_book_bittrex_url,
        EXCHANGE.KRAKEN: get_order_book_kraken_url,
        EXCHANGE.POLONIEX: get_order_book_poloniex_url,
        EXCHANGE.BINANCE: get_order_book_binance_url
    }[exchange_id]