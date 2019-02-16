from enums.exchange import EXCHANGE

from huobi.socket_api import SubscriptionHuobi, parse_socket_update_huobi
from bittrex.socket_api import SubscriptionBittrex, parse_socket_update_bittrex
from binance.socket_api import SubscriptionBinance, parse_socket_update_binance
from poloniex.socket_api import SubscriptionPoloniex, parse_socket_update_poloniex


def get_subcribtion_by_exchange(exchange_id):
    return {
        EXCHANGE.POLONIEX: SubscriptionPoloniex,
        EXCHANGE.HUOBI: SubscriptionHuobi,
        EXCHANGE.BINANCE: SubscriptionBinance,
        EXCHANGE.BITTREX: SubscriptionBittrex
    }[exchange_id]


def parse_update_by_exchanges(exchange_id, order_book_delta):
    parse_method = {
        EXCHANGE.POLONIEX: parse_socket_update_poloniex,
        EXCHANGE.HUOBI: parse_socket_update_huobi,
        EXCHANGE.BINANCE: parse_socket_update_binance,
        EXCHANGE.BITTREX: parse_socket_update_bittrex
    }[exchange_id]

    return parse_method(order_book_delta)
