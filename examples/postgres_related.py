import csv
from collections import defaultdict

from data.trade import Trade

from utils.time_utils import get_now_seconds_utc
from utils.key_utils import load_keys, get_key_by_exchange

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from enums.currency_pair import CURRENCY_PAIR

from dao.db import save_order_into_pg, init_pg_connection, is_order_present_in_order_history, \
    is_trade_present_in_trade_history

from constants import DB_HOST, DB_PORT, DB_NAME, API_KEY_PATH

from analysis.data_load_for_profit_report import load_recent_huobi_trades_to_db, \
    wrap_with_progress_bar, save_to_pg_adapter
from bittrex.currency_utils import get_currency_pair_to_bittrex

from huobi.currency_utils import get_currency_pair_to_huobi
from huobi.order_history import get_order_history_huobi


def test_order_presence():
    pg_conn = init_pg_connection(_db_host=DB_HOST, _db_port=DB_PORT)
    # 6479142
    ts = get_now_seconds_utc()
    some_trade = Trade(DEAL_TYPE.BUY, EXCHANGE.BINANCE, CURRENCY_PAIR.BTC_TO_STRAT, price=0.001184, volume=2.08,
                       order_book_time=ts, create_time=ts, execute_time=ts, order_id='whatever')

    res = is_order_present_in_order_history(pg_conn, some_trade, table_name="tmp_binance_orders")

    print res


def test_trade_present():
    pg_conn = init_pg_connection(_db_host=DB_HOST, _db_port=DB_PORT)
    # 6479142
    ts = 1516142509
    trade = Trade(DEAL_TYPE.BUY, EXCHANGE.BINANCE, CURRENCY_PAIR.BTC_TO_STRAT, price=0.001184, volume=2.08,
                  order_book_time=ts, create_time=ts, execute_time=ts, order_id='whatever')

    res = is_trade_present_in_trade_history(pg_conn, trade, table_name="tmp_history_trades")

    print res


def test_insert_order():
    from enums.exchange import EXCHANGE
    from enums.deal_type import DEAL_TYPE
    from enums.currency_pair import CURRENCY_PAIR
    wtf = Trade(DEAL_TYPE.SELL, EXCHANGE.POLONIEX, CURRENCY_PAIR.BTC_TO_ARDR, 0.00001, 10.4, 1516039961, 1516039961)
    pg_conn = init_pg_connection(_db_host=DB_HOST, _db_port=DB_PORT, _db_name=DB_NAME)
    save_order_into_pg(wtf, pg_conn)


def load_trades_from_csv_to_db():
    file_name = "all_orders.csv"
    start_time = -1
    end_time = -2

    pg_conn = init_pg_connection(_db_host=DB_HOST, _db_port=DB_PORT, _db_name=DB_NAME)

    bittrex_order_by_pair = defaultdict(list)

    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            new_trade = Trade.from_bittrex_scv(row)
            if start_time <= new_trade.create_time <= end_time:
                bittrex_order_by_pair[new_trade.pair_id].append(new_trade)

    unique_only = True

    for pair_id in bittrex_order_by_pair:
        headline = "Loading bittrex trades - {p}".format(p=get_currency_pair_to_bittrex(pair_id))
        wrap_with_progress_bar(headline, bittrex_order_by_pair[pair_id], save_to_pg_adapter, pg_conn,
                               unique_only, is_trade_present_in_trade_history,
                               init_arbitrage_id=-20, table_name="arbitrage_trades")


def test_trade_history_huobi_methods():

    load_keys(API_KEY_PATH)
    key = get_key_by_exchange(EXCHANGE.HUOBI)

    time_end = get_now_seconds_utc()
    time_start = 0 # time_end - POLL_TIMEOUT

    pair_name = get_currency_pair_to_huobi(CURRENCY_PAIR.BTC_TO_LSK)

    huobi_orders_by_pair = get_order_history_huobi(key, pair_name, time_start, time_end)

    for pair_id in huobi_orders_by_pair:
        pair_name = get_currency_pair_to_huobi(pair_id)
        print "PAIR NAME: ", pair_name
        for b in huobi_orders_by_pair[pair_id]:
            print b

    res, order_history = get_order_history_huobi(key, pair_name, time_start, time_end)
    if len(order_history) > 0:
        for b in order_history:
            print b
    pg_conn = init_pg_connection(_db_host=DB_HOST, _db_port=DB_PORT, _db_name=DB_NAME)

    load_recent_huobi_trades_to_db(pg_conn, time_start, time_end, unique_only=True)
