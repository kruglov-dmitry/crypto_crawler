from enums.exchange import EXCHANGE
from binance.constants import BINANCE_CURRENCY_PAIRS
from binance.market_utils import get_trades_history_binance

from poloniex.order_history import get_order_history_poloniex
from bittrex.order_history import get_order_history_bittrex
from binance.order_history import get_order_history_binance

from poloniex.currency_utils import get_currency_pair_from_poloniex, get_currency_pair_to_poloniex
from binance.currency_utils import get_currency_pair_from_binance
from bittrex.currency_utils import get_currency_pair_to_bittrex

from utils.key_utils import get_key_by_exchange
from data.Trade import Trade
from dao.db import save_order_into_pg, is_order_present_in_order_history, is_trade_present_in_trade_history
from utils.time_utils import get_now_seconds_utc, sleep_for
from collections import defaultdict
from constants import START_OF_TIME

from tqdm import tqdm


def fetch_trades_history_to_db(pg_conn, start_time):
    load_recent_binance_orders_to_db(pg_conn, start_time)
    load_recent_binance_trades_to_db(pg_conn, start_time)
    load_recent_poloniex_trades_to_db(pg_conn, start_time)
    load_recent_bittrex_trades_to_db(pg_conn, start_time)


def wrap_with_progress_bar(descr, input_array, functor, *args, **kwargs):
    for entry in tqdm(input_array, desc=descr):
        functor(entry, *args, **kwargs)


def get_recent_binance_orders():
    key = get_key_by_exchange(EXCHANGE.BINANCE)

    binance_order = []
    limit = 500
    for pair_name in BINANCE_CURRENCY_PAIRS:
        err_code, json_document = get_order_history_binance(key, pair_name, limit)
        for entry in json_document:
            binance_order.append(Trade.from_binance(entry))
        sleep_for(1)

    return binance_order


def save_to_pg_adapter(order, pg_conn, unique_only, table_name, init_arbitrage_id):
    order.arbitrage_id = init_arbitrage_id
    if unique_only:
        if is_order_present_in_order_history(pg_conn, order, table_name):
            return
    save_order_into_pg(order, pg_conn, table_name)


def load_recent_binance_orders_to_db(pg_conn, start_time, unique_only=True):
    binance_orders = get_recent_binance_orders()

    binance_orders = [x for x in binance_orders if x.create_time >= start_time]

    wrap_with_progress_bar("Loading recent binance orders to db...", binance_orders, save_to_pg_adapter, pg_conn,
                           unique_only, init_arbitrage_id=-10, table_name="binance_order_history")


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


def load_recent_binance_trades_to_db(pg_conn, start_time, unique_only=True):
    binance_trades = get_recent_binance_trades()

    binance_trades = [x for x in binance_trades if x.create_time >= start_time]

    wrap_with_progress_bar("Loading recent binance trades to db ...", binance_trades, save_to_pg_adapter, pg_conn, unique_only,
                           init_arbitrage_id=-20, table_name="trades_history")


def get_recent_poloniex_trades(start_time=START_OF_TIME):
    now_time = get_now_seconds_utc()

    key = get_key_by_exchange(EXCHANGE.POLONIEX)
    error_code, json_document = get_order_history_poloniex(key, pair_name='all', time_start=start_time,
                                                           time_end=now_time, limit=10000)
    poloniex_orders_by_pair = defaultdict(list)
    for pair_name in json_document:
        for entry in json_document[pair_name]:
            pair_id = get_currency_pair_from_poloniex(pair_name)
            yet_more_trade = Trade.from_poloniex_history(entry, pair_name)
            if yet_more_trade.create_time >= start_time:
                poloniex_orders_by_pair[pair_id].append(yet_more_trade)

    return poloniex_orders_by_pair


def load_recent_poloniex_trades_to_db(pg_conn, start_time, unique_only=True):
    poloniex_orders_by_pair = get_recent_poloniex_trades(start_time)

    for pair_id in poloniex_orders_by_pair:
        headline = "Loading poloniex trades - {p}".format(p=get_currency_pair_to_poloniex(pair_id))
        wrap_with_progress_bar(headline, poloniex_orders_by_pair[pair_id], save_to_pg_adapter, pg_conn, unique_only,
                               init_arbitrage_id=-20, table_name="trades_history")


def get_recent_bittrex_trades(start_time=START_OF_TIME):
    key = get_key_by_exchange(EXCHANGE.BITTREX)
    error_code, json_document = get_order_history_bittrex(key, pair_name='all')

    bittrex_order_by_pair = defaultdict(list)
    for entry in json_document["result"]:
        new_trade = Trade.from_bittrex_history(entry)
        if new_trade.create_time >= start_time:
            bittrex_order_by_pair[new_trade.pair_id].append(new_trade)

    return bittrex_order_by_pair


def load_recent_bittrex_trades_to_db(pg_conn, start_time, unique_only=True):
    bittrex_order_by_pair = get_recent_bittrex_trades(start_time)

    for pair_id in bittrex_order_by_pair:
        headline = "Loading bittrex trades - {p}".format(p=get_currency_pair_to_bittrex(pair_id))
        wrap_with_progress_bar(headline, bittrex_order_by_pair[pair_id], save_to_pg_adapter, pg_conn, unique_only,
                               init_arbitrage_id=-20, table_name="trades_history")