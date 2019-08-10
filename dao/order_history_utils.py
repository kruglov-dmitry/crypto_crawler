from utils.debug_utils import print_to_console, LOG_ALL_ERRORS

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

    method_by_exchange = {
        EXCHANGE.BITTREX: get_order_history_bittrex,
        EXCHANGE.KRAKEN: get_order_history_kraken,
        EXCHANGE.POLONIEX: get_order_history_poloniex,
        EXCHANGE.BINANCE: get_order_history_binance,
        EXCHANGE.HUOBI: get_order_history_huobi
    }

    if exchange_id in method_by_exchange:
        get_order_history = method_by_exchange[exchange_id]
        res = get_order_history(key, pair_name)
    else:
        msg = "get_open_orders_by_exchange - Unknown exchange! {idx}".format(idx=exchange_id)
        print_to_console(msg, LOG_ALL_ERRORS)

    return res