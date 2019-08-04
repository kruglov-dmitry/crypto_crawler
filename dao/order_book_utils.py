from collections import defaultdict

from binance.constants import BINANCE_CURRENCY_PAIRS
from binance.order_book_utils import get_order_book_binance, get_order_book_binance_url, \
    get_order_book_binance_result_processor

from bittrex.constants import BITTREX_CURRENCY_PAIRS
from bittrex.order_book_utils import get_order_book_bittrex, get_order_book_bittrex_url, \
    get_order_book_bittrex_result_processor
from bittrex.socket_api import get_order_book_bittrex_through_socket

from kraken.constants import KRAKEN_CURRENCY_PAIRS
from kraken.order_book_utils import get_order_book_kraken, get_order_book_kraken_url, \
    get_order_book_kraken_result_processor

from poloniex.constants import POLONIEX_CURRENCY_PAIRS
from poloniex.order_book_utils import get_order_book_poloniex, get_order_book_poloniex_url, \
    get_order_book_poloniex_result_processor

from huobi.constants import HUOBI_CURRENCY_PAIRS
from huobi.order_book_utils import get_order_book_huobi, get_order_book_huobi_url, \
    get_order_book_huobi_result_processor

from constants import HTTP_TIMEOUT_SECONDS, HTTP_TIMEOUT_ORDER_BOOK_ARBITRAGE
from data_access.classes.work_unit import WorkUnit
from enums.currency_pair import CURRENCY_PAIR
from enums.exchange import EXCHANGE

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.time_utils import get_now_seconds_utc
from logging_tools.arbitrage_between_pair_logging import log_dublicative_order_book


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
        EXCHANGE.BINANCE: get_order_book_binance_result_processor,
        EXCHANGE.HUOBI: get_order_book_huobi_result_processor
    }[exchange_id]


def get_order_book_speedup(date_start, date_end, processor):

    order_book_async_requests = []

    for exchange_id in EXCHANGE.values():
        for pair_id in CURRENCY_PAIR.values():

            pair_name = get_currency_pair_name_by_exchange_id(pair_id, exchange_id)
            if pair_name:
                method_for_url = get_order_book_url_by_exchange_id(exchange_id)
                request_url = method_for_url(pair_name)
                constructor = get_order_book_constructor_by_exchange_id(exchange_id)

                order_book_async_requests.append(WorkUnit(request_url, constructor, pair_name, date_end))

    return processor.process_async_get(order_book_async_requests, HTTP_TIMEOUT_SECONDS)


def get_order_books_for_arbitrage_pair(cfg, date_end, processor):

    order_book_async_requests = []

    for exchange_id in [cfg.sell_exchange_id, cfg.buy_exchange_id]:
        pair_name = get_currency_pair_name_by_exchange_id(cfg.pair_id, exchange_id)
        if pair_name is None:
            print "UNSUPPORTED COMBINATION OF PAIR ID AND EXCHANGE", cfg.pair_id, exchange_id
            assert pair_name is None

        method_for_url = get_order_book_url_by_exchange_id(exchange_id)
        request_url = method_for_url(pair_name)
        constructor = get_order_book_constructor_by_exchange_id(exchange_id)

        order_book_async_requests.append(WorkUnit(request_url, constructor, pair_name, date_end))

    return processor.process_async_get(order_book_async_requests, timeout=HTTP_TIMEOUT_ORDER_BOOK_ARBITRAGE)


def get_order_book_sync_and_slow():

    all_order_book = defaultdict(list)

    timest = get_now_seconds_utc()

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

    for currency in HUOBI_CURRENCY_PAIRS:
        order_book = get_order_book_huobi(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.HUOBI].append(order_book)

    return all_order_book


def get_order_book_method_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_order_book_bittrex_through_socket,
        EXCHANGE.KRAKEN: get_order_book_kraken,
        EXCHANGE.POLONIEX: get_order_book_poloniex,
        EXCHANGE.BINANCE: get_order_book_binance,
        EXCHANGE.HUOBI: get_order_book_huobi
    }[exchange_id]


def get_order_book_url_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_order_book_bittrex_url,
        EXCHANGE.KRAKEN: get_order_book_kraken_url,
        EXCHANGE.POLONIEX: get_order_book_poloniex_url,
        EXCHANGE.BINANCE: get_order_book_binance_url,
        EXCHANGE.HUOBI: get_order_book_huobi_url
    }[exchange_id]


def get_order_book(exchange_id, pair_id):
    timest = get_now_seconds_utc()

    pair_name = get_currency_pair_name_by_exchange_id(pair_id, exchange_id)
    if pair_name is None:
        print "UNSUPPORTED COMBINATION OF PAIR ID AND EXCHANGE", pair_id, exchange_id
        assert pair_name is None

    method = get_order_book_method_by_exchange_id(exchange_id)

    return method(pair_name, timest)


def is_order_book_expired(log_file_name, order_book, local_cache, msg_queue):

    prev_order_book = local_cache.get_last_order_book(order_book.pair_id, order_book.exchange_id)

    if prev_order_book is None:
        return False

    total_asks = len(order_book.ask)
    number_of_same_asks = len(set(order_book.ask).intersection(prev_order_book.ask))

    total_bids = len(order_book.bid)
    number_of_same_bids = len(set(order_book.bid).intersection(prev_order_book.bid))

    if total_asks == number_of_same_asks or total_bids == number_of_same_bids:
        # FIXME NOTE: probably we can loose a bit this condition - for example check that order book
        # should differ for more than 10% of bids OR asks ?
        log_dublicative_order_book(log_file_name, order_book, prev_order_book, msg_queue)
        return True

    return False
