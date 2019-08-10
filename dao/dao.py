#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.buy_utils import add_buy_order_bittrex, add_buy_order_bittrex_url
from bittrex.sell_utils import add_sell_order_bittrex, add_sell_order_bittrex_url
from bittrex.market_utils import cancel_order_bittrex, parse_order_id_bittrex
from bittrex.currency_utils import get_currency_pair_to_bittrex

from kraken.buy_utils import add_buy_order_kraken, add_buy_order_kraken_url
from kraken.sell_utils import add_sell_order_kraken, add_sell_order_kraken_url
from kraken.market_utils import cancel_order_kraken, parse_order_id_kraken
from kraken.currency_utils import get_currency_pair_to_kraken

from poloniex.buy_utils import add_buy_order_poloniex, add_buy_order_poloniex_url
from poloniex.sell_utils import add_sell_order_poloniex, add_sell_order_poloniex_url
from poloniex.market_utils import cancel_order_poloniex, parse_order_id_poloniex
from poloniex.currency_utils import get_currency_pair_to_poloniex

from binance.buy_utils import add_buy_order_binance, add_buy_order_binance_url
from binance.sell_utils import add_sell_order_binance, add_sell_order_binance_url
from binance.market_utils import cancel_order_binance, parse_order_id_binance
from binance.currency_utils import get_currency_pair_to_binance

from huobi.currency_utils import get_currency_pair_to_huobi
from huobi.buy_utils import add_buy_order_huobi, add_buy_order_huobi_url
from huobi.sell_utils import add_sell_order_huobi, add_sell_order_huobi_url
from huobi.market_utils import cancel_order_huobi, parse_order_id_huobi


from enums.exchange import EXCHANGE
from enums.status import STATUS
from enums.deal_type import DEAL_TYPE

from utils.key_utils import get_key_by_exchange
from utils.debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file


def assert_trade_type(trade, expected_type):
    if trade.trade_type != expected_type:

        msg = "Deal type do NOT correspond to method invocation. {d}".format(d=trade)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

        assert trade.trade_type != expected_type


def log_error_unknown_exchange(func_name, details):
    msg = "{func_name} - Unknown exchange! Details: {res}".format(func_name=func_name, res=details)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, "error.log")


def buy_by_exchange(trade):
    res = STATUS.FAILURE, None
    assert_trade_type(trade, DEAL_TYPE.BUY)

    key = get_key_by_exchange(trade.exchange_id)

    methods_by_exchange = {
        EXCHANGE.BITTREX: (get_currency_pair_to_bittrex, add_buy_order_bittrex),
        EXCHANGE.KRAKEN: (get_currency_pair_to_kraken, add_buy_order_kraken),
        EXCHANGE.POLONIEX: (get_currency_pair_to_poloniex, add_buy_order_poloniex),
        EXCHANGE.BINANCE: (get_currency_pair_to_binance, add_buy_order_binance),
        EXCHANGE.HUOBI: (get_currency_pair_to_huobi, add_buy_order_huobi)
    }

    if trade.exchange_id in methods_by_exchange:
        get_currency_pair, add_buy_order = methods_by_exchange[trade.exchange_id]
        currency = get_currency_pair(trade.pair_id)
        res = add_buy_order(key, currency, trade.price, trade.volume)
    else:
        log_error_unknown_exchange("buy_by_exchange", trade)

    return res


def sell_by_exchange(trade):
    res = STATUS.FAILURE, None

    assert_trade_type(trade, DEAL_TYPE.SELL)

    key = get_key_by_exchange(trade.exchange_id)

    methods_by_exchange = {
        EXCHANGE.BITTREX: (get_currency_pair_to_bittrex, add_sell_order_bittrex),
        EXCHANGE.KRAKEN: (get_currency_pair_to_kraken, add_sell_order_kraken),
        EXCHANGE.POLONIEX: (get_currency_pair_to_poloniex, add_sell_order_poloniex),
        EXCHANGE.BINANCE: (get_currency_pair_to_binance, add_sell_order_binance),
        EXCHANGE.HUOBI: (get_currency_pair_to_huobi, add_sell_order_huobi)
    }
    if trade.exchange_id in methods_by_exchange:
        get_currency_pair, add_sell_order = methods_by_exchange[trade.exchange_id]
        currency = get_currency_pair(trade.pair_id)
        res = add_sell_order(key, currency, trade.price, trade.volume)
    else:
        log_error_unknown_exchange("sell_by_exchange", trade)

    return res


def cancel_by_exchange(trade):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)

    methods_by_exchange = {
        EXCHANGE.BITTREX: cancel_order_bittrex,
        EXCHANGE.KRAKEN: cancel_order_kraken,
        EXCHANGE.POLONIEX: cancel_order_poloniex,
        EXCHANGE.HUOBI: cancel_order_huobi
    }

    if trade.exchange_id in methods_by_exchange:
        res = methods_by_exchange[trade.exchange_id](key, trade.order_id)
    elif trade.exchange_id == EXCHANGE.BINANCE:
        pair_name = get_currency_pair_to_binance(trade.pair_id)
        res = cancel_order_binance(key, pair_name, trade.order_id)
    else:
        log_error_unknown_exchange("cancel_by_exchange", trade)

    return res


def get_method_for_create_url_trade_by_exchange_id(trade):
    return {
        DEAL_TYPE.BUY: {
            EXCHANGE.BINANCE: add_buy_order_binance_url,
            EXCHANGE.BITTREX: add_buy_order_bittrex_url,
            EXCHANGE.POLONIEX: add_buy_order_poloniex_url,
            EXCHANGE.KRAKEN: add_buy_order_kraken_url,
            EXCHANGE.HUOBI: add_buy_order_huobi_url
        },
        DEAL_TYPE.SELL: {
            EXCHANGE.BINANCE: add_sell_order_binance_url,
            EXCHANGE.BITTREX: add_sell_order_bittrex_url,
            EXCHANGE.POLONIEX: add_sell_order_poloniex_url,
            EXCHANGE.KRAKEN: add_sell_order_kraken_url,
            EXCHANGE.HUOBI: add_sell_order_huobi_url
        }
    }[trade.trade_type][trade.exchange_id]


def parse_order_id(exchange_id, json_document):

    method = {
        EXCHANGE.POLONIEX: parse_order_id_poloniex,
        EXCHANGE.BITTREX: parse_order_id_bittrex,
        EXCHANGE.BINANCE: parse_order_id_binance,
        EXCHANGE.KRAKEN: parse_order_id_kraken,
        EXCHANGE.HUOBI: parse_order_id_huobi
    }[exchange_id]

    return method(json_document)
