from enums.exchange import EXCHANGE
from binance.constants import BINANCE_CURRENCY_PAIRS
from binance.market_utils import get_order_history_for_time_interval_binance, get_trades_history_binance
from poloniex.market_utils import get_order_history_for_time_interval_poloniex
from poloniex.currency_utils import get_currency_pair_from_poloniex
from binance.currency_utils import get_currency_pair_from_binance
from bittrex.market_utils import get_order_history_for_time_interval_bittrex

from utils.key_utils import get_key_by_exchange
from data.Trade import Trade
from dao.db import save_order_into_pg, is_order_present_in_order_history
from utils.time_utils import get_now_seconds_utc
from collections import defaultdict


def get_recent_binance_orders():
    key = get_key_by_exchange(EXCHANGE.BINANCE)
    from utils.time_utils import sleep_for
    binance_order = []
    limit = 500
    for pair_name in BINANCE_CURRENCY_PAIRS:
        err_code, json_document = get_order_history_for_time_interval_binance(key, pair_name, limit)
        for entry in json_document:
            binance_order.append(Trade.from_binance(entry))
        sleep_for(1)

    return binance_order


def load_recent_binance_orders_to_db(pg_conn, unique_only=True):
    binance_orders = get_recent_binance_orders()

    for bb in binance_orders:
        bb.arbitrage_id = -10
        if unique_only:
            if is_order_present_in_order_history(pg_conn, bb, table_name="binance_order_history"):
                continue
        save_order_into_pg(bb, pg_conn, table_name="binance_order_history")


def get_recent_binance_trades():
    key = get_key_by_exchange(EXCHANGE.BINANCE)

    last_order_id = None  # 19110542000
    limit = 200

    binance_order = []
    for pair_name in BINANCE_CURRENCY_PAIRS:
        error_code, json_document = get_trades_history_binance(key, pair_name, limit, last_order_id)

        for entry in json_document:
            binance_order.append(Trade.from_binance_history(entry, pair_name))

    return binance_order


def load_recent_binance_trades_to_db(pg_conn, unique_only=True):
    binance_orders = get_recent_binance_trades()

    for bb in binance_orders:
        bb.arbitrage_id = -20
        if unique_only:
            if is_trade_present_in_trade_history(pg_conn, bb, table_name="trades_history"):
                continue
        save_order_into_pg(bb, pg_conn, table_name="trades_history")


def get_recent_poloniex_trades():
    now_time = get_now_seconds_utc()
    two_days_ago = now_time - 4 * 24 * 60 * 60
    key = get_key_by_exchange(EXCHANGE.POLONIEX)
    error_code, json_document = get_order_history_for_time_interval_poloniex(key, pair_name='all',
                                                                             time_start=two_days_ago,
                                                                             time_end=now_time, limit=10000)
    poloniex_orders_by_pair = defaultdict(list)
    for pair_name in json_document:
        for entry in json_document[pair_name]:
            pair_id = get_currency_pair_from_poloniex(pair_name)
            poloniex_orders_by_pair[pair_id].append(Trade.from_poloniex_history(entry, pair_name))

    return poloniex_orders_by_pair


def load_recent_poloniex_trades_to_db(pg_conn, unique_only=True):
    poloniex_orders_by_pair = get_recent_poloniex_trades()

    for b in poloniex_orders_by_pair:
        for bb in poloniex_orders_by_pair[b]:
            bb.arbitrage_id = -30
            if unique_only:
                if is_trade_present_in_trade_history(pg_conn, bb, table_name="trades_history"):
                    continue
            save_order_into_pg(bb, pg_conn, table_name="trades_history")


def get_recent_bittrex_trades():
    key = get_key_by_exchange(EXCHANGE.BITTREX)
    error_code, json_document = get_order_history_for_time_interval_bittrex(key, pair_name='all')

    bittrex_order_by_pair = defaultdict(list)
    for entry in json_document["result"]:
        new_trade = Trade.from_bittrex_history(entry)
        bittrex_order_by_pair[new_trade.pair_id].append(new_trade)

    return bittrex_order_by_pair


def load_recent_bittrex_trades_to_db(pg_conn, unique_only=True):
    bittrex_order_by_pair = get_recent_bittrex_trades()

    for b in bittrex_order_by_pair:
        for bb in bittrex_order_by_pair[b]:
            if unique_only:
                if is_trade_present_in_trade_history(pg_conn, bb, table_name="trades_history"):
                    continue
            save_order_into_pg(bb, pg_conn, table_name="trades_history")