from debug_utils import print_to_console, LOG_ALL_ERRORS

from enums.exchange import EXCHANGE
from enums.status import STATUS

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.key_utils import get_key_by_exchange

from bittrex.order_history import get_order_history_bittrex
from kraken.order_history import get_order_history_kraken
from poloniex.order_history import get_order_history_poloniex
from binance.order_history import get_order_history_binance
from huobi.order_history import get_order_history_huobi


def get_order_history_by_exchange(exchange_id, pair_id):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(exchange_id)

    pair_name = get_currency_pair_name_by_exchange_id(pair_id, exchange_id)

    if exchange_id == EXCHANGE.BITTREX:
        res = get_order_history_bittrex(key, pair_name)
    elif exchange_id == EXCHANGE.KRAKEN:
        res = get_order_history_kraken(key, pair_name)
    elif exchange_id == EXCHANGE.POLONIEX:
        res = get_order_history_poloniex(key, pair_name)
    elif exchange_id == EXCHANGE.BINANCE:
        res = get_order_history_binance(key, pair_name)
    elif exchange_id == EXCHANGE.HUOBI:
        res = get_order_history_huobi(key, pair_name)
    else:
        msg = "get_open_orders_by_exchange - Unknown exchange! {idx}".format(idx=exchange_id)
        print_to_console(msg, LOG_ALL_ERRORS)

    return res