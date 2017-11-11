from utils.time_utils import get_now_seconds

#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.constants import BITTREX_CURRENCIES
from kraken.constants import KRAKEN_CURRENCY_PAIRS
from poloniex.constants import POLONIEX_CURRENCIES

from bittrex.ticker_utils import get_ticker_bittrex
from kraken.ticker_utils import get_ticker_kraken
from poloniex.ticker_utils import get_ticker_poloniex

from bittrex.ohlc_utils import get_ohlc_bittrex
from kraken.ohlc_utils import get_ohlc_kraken
from poloniex.ohlc_utils import get_ohlc_poloniex

from bittrex.order_book_utils import get_order_book_bittrex
from kraken.order_book_utils import get_order_book_kraken
from poloniex.order_book_utils import get_order_book_poloniex

from bittrex.history_utils import get_history_bittrex
from kraken.history_utils import get_history_kraken
from poloniex.history_utils import get_history_poloniex

from bittrex.market_utils import add_buy_order_bittrex, add_sell_order_bittrex, cancel_order_bittrex, \
    get_balance_bittrex
from kraken.market_utils import add_buy_order_kraken, add_sell_order_kraken, cancel_order_kraken, \
    get_balance_kraken
from poloniex.market_utils import add_buy_order_poloniex, add_sell_order_poloniex, cancel_order_poloniex, \
    get_balance_poloniex

from utils.currency_utils import get_currency_pair_to_bittrex, get_currency_pair_to_kraken, \
    get_currency_pair_to_poloniex

from enums.exchange import EXCHANGE
from enums.status import STATUS
from utils.key_utils import get_key_by_exchange

from collections import defaultdict

from data.BalanceState import BalanceState

from utils.currency_utils import get_currency_pair_from_bittrex, get_currency_pair_from_kraken, get_currency_pair_from_poloniex

import copy


def get_ticker():

    timest = get_now_seconds()

    bittrex_tickers = {}
    for currency in BITTREX_CURRENCIES:
        ticker = get_ticker_bittrex(currency, timest)
        if ticker is not None:
            bittrex_tickers[ticker.pair_id] = ticker

    kraken_tickers = {}
    for currency in KRAKEN_CURRENCY_PAIRS:
        ticker = get_ticker_kraken(currency, timest)
        if ticker is not None:
            kraken_tickers[ticker.pair_id] = ticker

    poloniex_tickers = {}
    for currency in POLONIEX_CURRENCIES:
        ticker = get_ticker_poloniex(currency, timest)
        if ticker is not None:
            poloniex_tickers[ticker.pair_id] = ticker

    return bittrex_tickers, kraken_tickers, poloniex_tickers


def get_ohlc():
    all_ohlc = []

    date_end = get_now_seconds()
    date_start = date_end

    for currency in BITTREX_CURRENCIES:
        period = "thirtyMin"
        all_ohlc += get_ohlc_bittrex(currency, date_end, date_start, period)

    for currency in KRAKEN_CURRENCY_PAIRS:
        period = 15
        all_ohlc += get_ohlc_kraken(currency, date_end, date_start, period)

    for currency in POLONIEX_CURRENCIES:
        period = 14400
        all_ohlc += get_ohlc_poloniex(currency, date_end, date_start, period)

    return all_ohlc


def get_order_book():

    all_order_book = defaultdict(list)

    timest = get_now_seconds()

    for currency in POLONIEX_CURRENCIES:
        order_book = get_order_book_poloniex(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.POLONIEX].append(order_book)

    for currency in KRAKEN_CURRENCY_PAIRS:
        order_book = get_order_book_kraken(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.KRAKEN].append(order_book)

    for currency in BITTREX_CURRENCIES:
        order_book = get_order_book_bittrex(currency, timest)
        if order_book is not None:
            all_order_book[EXCHANGE.BITTREX].append(order_book)

    return all_order_book


def get_order_book_by_pair(pair_id):
    all_order_book = defaultdict(list)

    timest = get_now_seconds()

    poloniex_pair_name = get_currency_pair_from_poloniex(pair_id)
    order_book = get_order_book_poloniex(poloniex_pair_name, timest)
    if order_book is not None:
        all_order_book[EXCHANGE.POLONIEX].append(order_book)

    kraken_pair_name = get_currency_pair_from_kraken(pair_id)
    order_book = get_order_book_kraken(kraken_pair_name, timest)
    if order_book is not None:
        all_order_book[EXCHANGE.KRAKEN].append(order_book)

    bittrex_pair_name = get_currency_pair_from_bittrex(pair_id)
    order_book = get_order_book_bittrex(bittrex_pair_name, timest)
    if order_book is not None:
        all_order_book[EXCHANGE.BITTREX].append(order_book)

    return all_order_book


def get_history(prev_time, now_time):
    all_history = []

    for currency in POLONIEX_CURRENCIES:
        all_history += get_history_poloniex(currency, prev_time, now_time)

    for currency in KRAKEN_CURRENCY_PAIRS:
        all_history += get_history_kraken(currency, prev_time, now_time)

    for currency in BITTREX_CURRENCIES:
        all_history += get_history_bittrex(currency, prev_time, now_time)

    return all_history


def buy_by_exchange(trade):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)
    if trade.exchange_id == EXCHANGE.BITTREX:
        currency = get_currency_pair_to_bittrex(trade.pair_id)
        res = add_buy_order_bittrex(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.KRAKEN:
        currency = get_currency_pair_to_kraken(trade.pair_id)
        res = add_buy_order_kraken(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.POLONIEX:
        currency = get_currency_pair_to_poloniex(trade.pair_id)
        res = add_buy_order_poloniex(key, currency, trade.price, trade.volume)
    else:
        print "buy_by_exchange - Unknown exchange! ", trade

    return res


def sell_by_exchange(trade):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)
    if trade.exchange_id == EXCHANGE.BITTREX:
        currency = get_currency_pair_to_bittrex(trade.pair_id)
        res = add_sell_order_bittrex(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.KRAKEN:
        currency = get_currency_pair_to_kraken(trade.pair_id)
        res = add_sell_order_kraken(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.POLONIEX:
        currency = get_currency_pair_to_poloniex(trade.pair_id)
        res = add_sell_order_poloniex(key, currency, trade.price, trade.volume)
    else:
        print "sell_by_exchange - Unknown exchange! ", trade

    return res


def cancel_by_exchange(trade):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)
    if trade.exchange_id == EXCHANGE.BITTREX:
        res = cancel_order_bittrex(key, trade.deal_id)
    elif trade.exchange_id == EXCHANGE.KRAKEN:
        res = cancel_order_kraken(key, trade.deal_id)
    elif trade.exchange_id == EXCHANGE.POLONIEX:
        res = cancel_order_poloniex(key, trade.deal_id)
    else:
        print "cancel_by_exchange - Unknown exchange! ", trade

    return res


def get_balance_by_exchange(exchange_id):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(exchange_id)

    if exchange_id == EXCHANGE.BITTREX:
        res = get_balance_bittrex(key)
    elif exchange_id == EXCHANGE.KRAKEN:
        res = get_balance_kraken(key)
    elif exchange_id == EXCHANGE.POLONIEX:
        res = get_balance_poloniex(key)
    else:
        print "show_balance_by_exchange - Unknown exchange! ", exchange_id

    return res


def get_updated_balance(balance_adjust_threshold, prev_balance):
    balance = {}

    for exchange_id in EXCHANGE.values():
        balance[exchange_id] = copy.deepcopy(prev_balance.balance_per_exchange[exchange_id])
        status_code, new_balance_value = get_balance_by_exchange(exchange_id)
        if status_code == STATUS.SUCCESS:
            balance[exchange_id] = new_balance_value

    return BalanceState(balance, balance_adjust_threshold)
