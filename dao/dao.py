from utils.time_utils import get_now_seconds_utc, get_now_seconds_local

#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.market_utils import add_buy_order_bittrex, add_sell_order_bittrex, cancel_order_bittrex, \
    get_balance_bittrex
from kraken.market_utils import add_buy_order_kraken, add_sell_order_kraken, cancel_order_kraken, \
    get_balance_kraken, get_orders_kraken
from poloniex.market_utils import add_buy_order_poloniex, add_sell_order_poloniex, cancel_order_poloniex, \
    get_balance_poloniex
from binance.market_utils import add_buy_order_binance, add_sell_order_binance, cancel_order_binance, \
    get_balance_binance

from utils.currency_utils import get_currency_pair_name_by_exchange_id

from bittrex.currency_utils import get_currency_pair_to_bittrex
from kraken.currency_utils import get_currency_pair_to_kraken
from poloniex.currency_utils import get_currency_pair_to_poloniex
from binance.currency_utils import get_currency_pair_to_binance

from enums.exchange import EXCHANGE
from enums.status import STATUS
from enums.currency_pair import CURRENCY_PAIR
from utils.key_utils import get_key_by_exchange
from utils.file_utils import log_to_file

from collections import defaultdict

from data.BalanceState import BalanceState

import copy


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
