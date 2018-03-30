#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.buy_utils import add_buy_order_bittrex, add_buy_order_bittrex_url
from bittrex.sell_utils import add_sell_order_bittrex, add_sell_order_bittrex_url
from bittrex.order_utils import get_open_orders_bittrix
from bittrex.market_utils import cancel_order_bittrex, parse_order_id_bittrex

from kraken.buy_utils import add_buy_order_kraken, add_buy_order_kraken_url
from kraken.sell_utils import add_sell_order_kraken, add_sell_order_kraken_url
from kraken.order_utils import get_open_orders_kraken
from kraken.market_utils import cancel_order_kraken, parse_order_id_kraken

from poloniex.buy_utils import add_buy_order_poloniex, add_buy_order_poloniex_url
from poloniex.sell_utils import add_sell_order_poloniex, add_sell_order_poloniex_url
from poloniex.order_utils import get_open_orders_poloniex
from poloniex.market_utils import cancel_order_poloniex, parse_order_id_poloniex

from binance.buy_utils import add_buy_order_binance, add_buy_order_binance_url
from binance.sell_utils import add_sell_order_binance, add_sell_order_binance_url
from binance.order_utils import get_open_orders_binance
from binance.market_utils import cancel_order_binance, parse_order_id_binance

from bittrex.currency_utils import get_currency_pair_to_bittrex
from kraken.currency_utils import get_currency_pair_to_kraken
from poloniex.currency_utils import get_currency_pair_to_poloniex
from binance.currency_utils import get_currency_pair_to_binance

from huobi.currency_utils import get_currency_pair_to_huobi
from huobi.buy_utils import add_buy_order_huobi, add_buy_order_huobi_url
from huobi.sell_utils import add_sell_order_huobi, add_sell_order_huobi_url
from huobi.market_utils import cancel_order_huobi, parse_order_id_huobi
from huobi.order_utils import get_open_orders_huobi


from enums.exchange import EXCHANGE
from enums.status import STATUS
from enums.deal_type import DEAL_TYPE

from utils.key_utils import get_key_by_exchange
from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file
from utils.currency_utils import get_currency_pair_name_by_exchange_id


def buy_by_exchange(trade):
    res = STATUS.FAILURE, None
    if trade.trade_type != DEAL_TYPE.BUY:

        msg = "Deal type do NOT correspond to method invocation. {d}".format(d=trade)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

        assert trade.trade_type != DEAL_TYPE.BUY

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
    elif trade.exchange_id == EXCHANGE.HUOBI:
        currency = get_currency_pair_to_huobi(trade.pair_id)
        res = add_buy_order_huobi(key, currency, trade.price, trade.volume)
    else:
        msg = "buy_by_exchange - Unknown exchange! Details: {res}".format(res=str(trade))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

    return res


def sell_by_exchange(trade):
    res = STATUS.FAILURE, None

    if trade.trade_type != DEAL_TYPE.SELL:

        msg = "Deal type do NOT correspond to method invocation. {d}".format(d=trade)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

        assert trade.trade_type != DEAL_TYPE.SELL

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
    elif trade.exchange_id == EXCHANGE.HUOBI:
        currency = get_currency_pair_to_huobi(trade.pair_id)
        res = add_sell_order_huobi(key, currency, trade.price, trade.volume)
    else:
        msg = "buy_by_exchange - Unknown exchange! Details: {res}".format(res=str(trade))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

    return res


def cancel_by_exchange(trade):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(trade.exchange_id)

    if trade.exchange_id == EXCHANGE.BITTREX:
        res = cancel_order_bittrex(key, trade.order_id)
    elif trade.exchange_id == EXCHANGE.KRAKEN:
        res = cancel_order_kraken(key, trade.order_id)
    elif trade.exchange_id == EXCHANGE.POLONIEX:
        res = cancel_order_poloniex(key, trade.order_id)
    elif trade.exchange_id == EXCHANGE.BINANCE:
        pair_name = get_currency_pair_to_binance(trade.pair_id)
        res = cancel_order_binance(key, pair_name, trade.order_id)
    elif trade.exchange_id == EXCHANGE.HUOBI:
        pair_name = get_currency_pair_to_huobi(trade.pair_id)
        res = cancel_order_huobi(key, pair_name, trade.order_id)
    else:
        msg = "cancel_by_exchange - Unknown exchange! Details: {res}".format(res=str(trade))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

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

    method = {EXCHANGE.POLONIEX: parse_order_id_poloniex,
              EXCHANGE.BITTREX: parse_order_id_bittrex,
              EXCHANGE.BINANCE: parse_order_id_binance,
              EXCHANGE.KRAKEN: parse_order_id_kraken,
              EXCHANGE.HUOBI: parse_order_id_huobi
            }[exchange_id]

    return method(json_document)


def get_open_orders_by_exchange(exchange_id, pair_id):
    key = get_key_by_exchange(exchange_id)
    pair_name = get_currency_pair_name_by_exchange_id(exchange_id, pair_id)

    method = {
        EXCHANGE.BITTREX: get_open_orders_bittrix,
        EXCHANGE.KRAKEN: get_open_orders_kraken,
        EXCHANGE.POLONIEX: get_open_orders_poloniex,
        EXCHANGE.BINANCE: get_open_orders_binance,
        EXCHANGE.HUOBI: get_open_orders_huobi
    }[exchange_id]

    res = method(key, pair_name)

    return res
