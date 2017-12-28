#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.buy_utils import add_buy_order_bittrex
from bittrex.sell_utils import add_sell_order_bittrex
from bittrex.order_utils import get_open_orders_bittrix
from bittrex.market_utils import cancel_order_bittrex

from kraken.buy_utils import add_buy_order_kraken
from kraken.sell_utils import add_sell_order_kraken
from kraken.order_utils import get_open_orders_kraken
from kraken.market_utils import cancel_order_kraken

from poloniex.buy_utils import add_buy_order_poloniex
from poloniex.sell_utils import add_sell_order_poloniex
from poloniex.order_utils import get_open_orders_poloniex
from poloniex.market_utils import cancel_order_poloniex

from binance.buy_utils import add_buy_order_binance
from binance.sell_utils import add_sell_order_binance
from binance.order_utils import get_open_orders_binance
from binance.market_utils import cancel_order_binance

from bittrex.currency_utils import get_currency_pair_to_bittrex
from kraken.currency_utils import get_currency_pair_to_kraken
from poloniex.currency_utils import get_currency_pair_to_poloniex
from binance.currency_utils import get_currency_pair_to_binance

from enums.exchange import EXCHANGE
from enums.status import STATUS

from utils.key_utils import get_key_by_exchange
from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file
from utils.currency_utils import get_currency_pair_name_by_exchange_id


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
    elif trade.exchange_id == EXCHANGE.BINANCE:
        currency = get_currency_pair_to_binance(trade.pair_id)
        res = add_buy_order_binance(key, currency, trade.price, trade.volume)
    else:
        msg = "buy_by_exchange - Unknown exchange! Details: {res}".format(res=str(trade))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

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
    elif trade.exchange_id == EXCHANGE.BINANCE:
        currency = get_currency_pair_to_binance(trade.pair_id)
        res = add_sell_order_binance(key, currency, trade.price, trade.volume)
    else:
        msg = "buy_by_exchange - Unknown exchange! Details: {res}".format(res=str(trade))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

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
        msg = "cancel_by_exchange - Unknown exchange! Details: {res}".format(res=str(trade))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

    return res


def get_open_orders_by_exchange(exchange_id, pair_id):
    key = get_key_by_exchange(exchange_id)
    pair_name = get_currency_pair_name_by_exchange_id(exchange_id, pair_id)

    method = {
        EXCHANGE.BITTREX: get_open_orders_bittrix,
        EXCHANGE.KRAKEN: get_open_orders_kraken,
        EXCHANGE.POLONIEX: get_open_orders_poloniex,
        EXCHANGE.BINANCE: get_open_orders_binance
    }[exchange_id]

    res = method(key, pair_name)

    return res


def get_updated_order_state(order_state):

    print "DAO: get_updated_order_state"
    raise

    new_order_state = {EXCHANGE.BITTREX: None,
                       EXCHANGE.POLONIEX: None,
                       EXCHANGE.KRAKEN: order_state[EXCHANGE.KRAKEN],
                       EXCHANGE.BINANCE: None}

    # krak_key = get_key_by_exchange(EXCHANGE.KRAKEN)
    # error_code, res = get_orders_kraken(krak_key)
    # if error_code == STATUS.SUCCESS:
    #    new_order_state[EXCHANGE.KRAKEN] = res

    return new_order_state
