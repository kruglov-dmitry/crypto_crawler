from utils.time_utils import get_now_seconds_utc, get_now_seconds_local

#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.constants import BITTREX_CURRENCIES
from kraken.constants import KRAKEN_CURRENCY_PAIRS
from poloniex.constants import POLONIEX_CURRENCIES
from binance.constants import BINANCE_CURRENCIES

from bittrex.ticker_utils import get_ticker_bittrex
from kraken.ticker_utils import get_ticker_kraken
from poloniex.ticker_utils import get_tickers_poloniex
from binance.ticker_utils import get_tickers_binance

from bittrex.ohlc_utils import get_ohlc_bittrex
from kraken.ohlc_utils import get_ohlc_kraken
from poloniex.ohlc_utils import get_ohlc_poloniex
from binance.ohlc_utils import get_ohlc_binance

from bittrex.order_book_utils import get_order_book_bittrex
from kraken.order_book_utils import get_order_book_kraken
from poloniex.order_book_utils import get_order_book_poloniex
from binance.order_book_utils import get_order_book_binance

from bittrex.history_utils import get_history_bittrex
from kraken.history_utils import get_history_kraken
from poloniex.history_utils import get_history_poloniex
# NO HISTORY FOR POLONIEX

from bittrex.market_utils import add_buy_order_bittrex, add_sell_order_bittrex, cancel_order_bittrex, \
    get_balance_bittrex
from kraken.market_utils import add_buy_order_kraken, add_sell_order_kraken, cancel_order_kraken, \
    get_balance_kraken, get_orders_kraken
from poloniex.market_utils import add_buy_order_poloniex, add_sell_order_poloniex, cancel_order_poloniex, \
    get_balance_poloniex
from binance.market_utils import add_buy_order_binance, add_sell_order_binance, cancel_order_binance, \
    get_balance_binance

from utils.currency_utils import get_currency_pair_to_bittrex, get_currency_pair_to_kraken, \
    get_currency_pair_to_poloniex, get_currency_pair_to_binance, get_currency_name_by_exchange_id

from enums.exchange import EXCHANGE
from enums.status import STATUS
from enums.currency_pair import CURRENCY_PAIR
from utils.key_utils import get_key_by_exchange
from utils.file_utils import log_to_file

from collections import defaultdict

from data.BalanceState import BalanceState

import copy


def get_ticker():
    all_tickers = {}

    timest = get_now_seconds_local()

    bittrex_tickers = {}
    for currency in BITTREX_CURRENCIES:
        ticker = get_ticker_bittrex(currency, timest)
        if ticker is not None:
            bittrex_tickers[ticker.pair_id] = ticker
    all_tickers[EXCHANGE.BITTREX] = bittrex_tickers

    kraken_tickers = {}
    for currency in KRAKEN_CURRENCY_PAIRS:
        ticker = get_ticker_kraken(currency, timest)
        if ticker is not None:
            kraken_tickers[ticker.pair_id] = ticker
    all_tickers[EXCHANGE.KRAKEN] = kraken_tickers

    # NOTE: poloniex return all tickers by single call
    poloniex_tickers = get_tickers_poloniex(POLONIEX_CURRENCIES, timest)
    all_tickers[EXCHANGE.POLONIEX] = poloniex_tickers

    # NOTE: binance return all tickers by single call
    binance_tickers = get_tickers_binance(BINANCE_CURRENCIES, timest)
    all_tickers[EXCHANGE.BINANCE] = binance_tickers

    # return bittrex_tickers, kraken_tickers, poloniex_tickers, binance_tickers
    return all_tickers


def get_ohlc(date_start, date_end):
    all_ohlc = []

    for currency in BITTREX_CURRENCIES:
        period = "thirtyMin"
        all_ohlc += get_ohlc_bittrex(currency, date_start, date_end, period)

    for currency in KRAKEN_CURRENCY_PAIRS:
        period = 15
        all_ohlc += get_ohlc_kraken(currency, date_start, date_end, period)

    for currency in POLONIEX_CURRENCIES:
        period = 14400
        all_ohlc += get_ohlc_poloniex(currency, date_start, date_end, period)

    for currency in BINANCE_CURRENCIES:
        period = "15m"
        all_ohlc += get_ohlc_binance(currency, date_start, date_end, period)

    return all_ohlc


def get_period_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: "thirtyMin",
        EXCHANGE.KRAKEN: 15,
        EXCHANGE.POLONIEX: 14400,
        EXCHANGE.BINANCE: "15m"
    }[exchange_id]


def get_ohlc_method_by_echange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_ohlc_bittrex,
        EXCHANGE.KRAKEN: get_ohlc_kraken,
        EXCHANGE.POLONIEX: get_ohlc_poloniex,
        EXCHANGE.BINANCE: get_ohlc_binance
    }[exchange_id]


def get_ohlc_speedup(date_start, date_end):
    num_of_requests = len(CURRENCY_PAIR.values()) * len(EXCHANGE.values())

    from gevent.pool import Pool as GPool
    import gevent
    pool = GPool(num_of_requests / 2)
    glets = []

    for pair_id in CURRENCY_PAIR.values():
        for exchange_id in EXCHANGE.values():
            pair_name = get_currency_name_by_exchange_id(pair_id, exchange_id)
            period = get_period_by_exchange_id(exchange_id)
            functor = get_ohlc_method_by_echange_id(exchange_id)

            with gevent.Timeout(10, False):
                g = pool.spawn(functor,
                               date_start, date_end, period)
                glets.append(g)
            pool.join()

    return [g.value for g in glets]

def get_order_book():

    all_order_book = defaultdict(list)

    timest = get_now_seconds_local()

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

    for currency in BINANCE_CURRENCIES:
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


def get_history(prev_time, now_time):
    all_history = []

    for currency in POLONIEX_CURRENCIES:
        all_history += get_history_poloniex(currency, prev_time, now_time)

    for currency in KRAKEN_CURRENCY_PAIRS:
        all_history += get_history_kraken(currency, prev_time, now_time)

    for currency in BITTREX_CURRENCIES:
        all_history += get_history_bittrex(currency, prev_time, now_time)

    # FIXME NOTE: not found binance history ???

    return all_history


def buy_by_exchange(trade, order_state):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)
    if trade.exchange_id == EXCHANGE.BITTREX:
        currency = get_currency_pair_to_bittrex(trade.pair_id)
        res = add_buy_order_bittrex(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.KRAKEN:
        currency = get_currency_pair_to_kraken(trade.pair_id)
        res = add_buy_order_kraken(key, currency, trade.price, trade.volume, order_state[EXCHANGE.KRAKEN])
    elif trade.exchange_id == EXCHANGE.POLONIEX:
        currency = get_currency_pair_to_poloniex(trade.pair_id)
        res = add_buy_order_poloniex(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.BINANCE:
        currency = get_currency_pair_to_binance(trade.pair_id)
        res = add_buy_order_binance(key, currency, trade.price, trade.volume)
    else:
        print "buy_by_exchange - Unknown exchange! ", trade

    return res


def sell_by_exchange(trade, order_state):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)
    if trade.exchange_id == EXCHANGE.BITTREX:
        currency = get_currency_pair_to_bittrex(trade.pair_id)
        res = add_sell_order_bittrex(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.KRAKEN:
        currency = get_currency_pair_to_kraken(trade.pair_id)
        res = add_sell_order_kraken(key, currency, trade.price, trade.volume, order_state[EXCHANGE.KRAKEN])
    elif trade.exchange_id == EXCHANGE.POLONIEX:
        currency = get_currency_pair_to_poloniex(trade.pair_id)
        res = add_sell_order_poloniex(key, currency, trade.price, trade.volume)
    elif trade.exchange_id == EXCHANGE.BINANCE:
        currency = get_currency_pair_to_binance(trade.pair_id)
        res = add_sell_order_binance(key, currency, trade.price, trade.volume)
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
    elif trade.exchange_id == EXCHANGE.BINANCE:
        pair_name = get_currency_pair_to_binance(trade.pair_id)
        res = cancel_order_binance(key, pair_name, trade.deal_id)
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
    elif exchange_id == EXCHANGE.BINANCE:
        res = get_balance_binance(key)
    else:
        print "show_balance_by_exchange - Unknown exchange! ", exchange_id

    return res


def get_updated_balance(balance_adjust_threshold, prev_balance):
    balance = {}

    for exchange_id in EXCHANGE.values():
        if exchange_id == EXCHANGE.KRAKEN or exchange_id == EXCHANGE.BINANCE:
            continue
        balance[exchange_id] = copy.deepcopy(prev_balance.balance_per_exchange[exchange_id])
        status_code, new_balance_value = get_balance_by_exchange(exchange_id)
        if status_code == STATUS.SUCCESS:
            balance[exchange_id] = new_balance_value
            log_to_file(new_balance_value, "debug.txt")

    return BalanceState(balance, balance_adjust_threshold)


def get_updated_order_state(order_state):
    new_order_state = {EXCHANGE.BITTREX: None,
                       EXCHANGE.POLONIEX: None,
                       EXCHANGE.KRAKEN: order_state[EXCHANGE.KRAKEN],
                       EXCHANGE.BINANCE: None}

    # krak_key = get_key_by_exchange(EXCHANGE.KRAKEN)
    # error_code, res = get_orders_kraken(krak_key)
    # if error_code == STATUS.SUCCESS:
    #    new_order_state[EXCHANGE.KRAKEN] = res

    return new_order_state
