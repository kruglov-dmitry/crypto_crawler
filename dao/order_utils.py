from enums.status import STATUS
from enums.exchange import EXCHANGE

from constants import HTTP_TIMEOUT_SECONDS

from bittrex.order_utils import get_open_orders_bittrix, get_open_orders_bittrex_result_processor, \
    get_open_orders_bittrix_post_details
from kraken.order_utils import get_open_orders_kraken, get_open_orders_kraken_post_details, \
    get_open_orders_kraken_result_processor
from poloniex.order_utils import get_open_orders_poloniex, get_open_orders_poloniex_post_details, \
    get_open_orders_poloniex_result_processor
from binance.order_utils import get_open_orders_binance, get_open_orders_binance_post_details, \
    get_open_orders_binance_result_processor

from data_access.ConnectionPool import WorkUnit

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.key_utils import get_key_by_exchange
from utils.file_utils import log_to_file
from utils.currency_utils import get_currency_pair_name_by_exchange_id


def get_open_orders_by_exchange(exchange_id, pair_id):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(exchange_id)

    if exchange_id == EXCHANGE.BITTREX:
        res = get_open_orders_bittrix(key, pair_id)
    elif exchange_id == EXCHANGE.KRAKEN:
        res = get_open_orders_kraken(key, pair_id)
    elif exchange_id == EXCHANGE.POLONIEX:
        res = get_open_orders_poloniex(key, pair_id)
    elif exchange_id == EXCHANGE.BINANCE:
        res = get_open_orders_binance(key, pair_id)
    else:
        msg = "get_open_orders_by_exchange - Unknown exchange! {idx}".format(idx=exchange_id)
        print_to_console(msg, LOG_ALL_ERRORS)

    return res


def get_open_orders_post_details_generator(exchange_id):
    return {
        EXCHANGE.BITTREX: get_open_orders_bittrix_post_details,
        EXCHANGE.KRAKEN: get_open_orders_kraken_post_details,
        EXCHANGE.POLONIEX: get_open_orders_poloniex_post_details,
        EXCHANGE.BINANCE: get_open_orders_binance_post_details
    }[exchange_id]


def get_open_orders_constructor_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_open_orders_bittrex_result_processor,
        EXCHANGE.KRAKEN: get_open_orders_kraken_result_processor,
        EXCHANGE.POLONIEX: get_open_orders_poloniex_result_processor,
        EXCHANGE.BINANCE: get_open_orders_binance_result_processor
    }[exchange_id]


def get_order_books_for_arbitrage_pair(cfg, processor):

    open_orders = []

    for exchange_id in [cfg.sell_exchange_id, cfg.buy_exchange_id]:
        key = get_key_by_exchange(exchange_id)
        pair_name = get_currency_pair_name_by_exchange_id(cfg.pair_id, exchange_id)

        method_for_url = get_open_orders_post_details_generator(exchange_id)
        post_details = method_for_url(key, pair_name)
        constructor = get_open_orders_constructor_by_exchange_id(exchange_id)

        wu = WorkUnit(post_details.final_url, constructor)
        wu.add_post_details(post_details)

        open_orders.append(wu)

    return processor.process_async_post(open_orders, HTTP_TIMEOUT_SECONDS)