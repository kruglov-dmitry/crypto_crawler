#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.buy_utils import add_buy_order_bittrex, add_buy_order_bittrex_url
from bittrex.sell_utils import add_sell_order_bittrex, add_sell_order_bittrex_url
from bittrex.order_utils import get_open_orders_bittrix
from bittrex.market_utils import cancel_order_bittrex, parse_deal_id_bittrex, parse_deal_id_bittrex_from_json

from kraken.buy_utils import add_buy_order_kraken, add_buy_order_kraken_url
from kraken.sell_utils import add_sell_order_kraken, add_sell_order_kraken_url
from kraken.order_utils import get_open_orders_kraken
from kraken.market_utils import cancel_order_kraken, parse_deal_id_kraken, parse_deal_id_kraken_from_json

from poloniex.buy_utils import add_buy_order_poloniex, add_buy_order_poloniex_url
from poloniex.sell_utils import add_sell_order_poloniex, add_sell_order_poloniex_url
from poloniex.order_utils import get_open_orders_poloniex
from poloniex.market_utils import cancel_order_poloniex, parse_deal_id_poloniex, parse_deal_id_poloniex_from_json

from binance.buy_utils import add_buy_order_binance, add_buy_order_binance_url
from binance.sell_utils import add_sell_order_binance, add_sell_order_binance_url
from binance.order_utils import get_open_orders_binance
from binance.market_utils import cancel_order_binance, parse_deal_id_binance, parse_deal_id_binance_from_json

from bittrex.currency_utils import get_currency_pair_to_bittrex
from kraken.currency_utils import get_currency_pair_to_kraken
from poloniex.currency_utils import get_currency_pair_to_poloniex
from binance.currency_utils import get_currency_pair_to_binance

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
        raise

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

    if trade.trade_type != DEAL_TYPE.SELL:
        msg = "Deal type do NOT correspond to method invocation. {d}".format(d=trade)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")
        raise

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


def get_method_for_create_url_trade_by_exchange_id(trade):
    return {
        DEAL_TYPE.BUY: {
            EXCHANGE.BINANCE: add_buy_order_binance_url,
            EXCHANGE.BITTREX: add_buy_order_bittrex_url,
            EXCHANGE.POLONIEX: add_buy_order_poloniex_url,
            EXCHANGE.KRAKEN: add_buy_order_kraken_url,
        },
        DEAL_TYPE.SELL: {
            EXCHANGE.BINANCE: add_sell_order_binance_url,
            EXCHANGE.BITTREX: add_sell_order_bittrex_url,
            EXCHANGE.POLONIEX: add_sell_order_poloniex_url,
            EXCHANGE.KRAKEN: add_sell_order_kraken_url,
        }
    }[trade.trade_type][trade.exchange_id]


def parse_deal_id_by_exchange_id(exchange_id, http_responce):

    method = {EXCHANGE.POLONIEX: parse_deal_id_poloniex,
              EXCHANGE.BITTREX: parse_deal_id_bittrex,
              EXCHANGE.BINANCE: parse_deal_id_binance,
              EXCHANGE.KRAKEN: parse_deal_id_kraken,
            }[exchange_id]

    return method(http_responce)

def parse_deal_id(exchange_id, json_document):

    method = {EXCHANGE.POLONIEX: parse_deal_id_poloniex_from_json,
              EXCHANGE.BITTREX: parse_deal_id_bittrex_from_json,
              EXCHANGE.BINANCE: parse_deal_id_binance_from_json,
              EXCHANGE.KRAKEN: parse_deal_id_kraken_from_json,
            }[exchange_id]

    return method(json_document)


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
