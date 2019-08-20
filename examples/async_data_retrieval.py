from profilehooks import timecall

from utils.time_utils import get_now_seconds_utc
from utils.key_utils import load_keys
from utils.debug_utils import LOG_ALL_DEBUG

from data_access.classes.connection_pool import ConnectionPool
from data.arbitrage_config import ArbitrageConfig

from dao.history_utils import get_history_speedup
from dao.ohlc_utils import get_ohlc_speedup, get_ohlc
from dao.order_book_utils import get_order_book_speedup
from dao.ticker_utils import get_ticker_speedup
from dao.order_utils import get_open_orders_for_arbitrage_pair

from enums.currency_pair import CURRENCY_PAIR
from enums.exchange import EXCHANGE

from constants import API_KEY_PATH


POLL_PERIOD_SECONDS = 900


@timecall
def get_ohlc_time_test():
    end_time = get_now_seconds_utc()
    start_time = end_time - 900

    get_ohlc(start_time, end_time)


@timecall
def get_ohlc_time_fast_test():
    processor = ConnectionPool()
    end_time = get_now_seconds_utc()
    start_time = end_time - 900
    return get_ohlc_speedup(start_time, end_time, processor)


@timecall
def get_ticker_time_fast():
    timest = get_now_seconds_utc()
    processor = ConnectionPool()
    return get_ticker_speedup(timest, processor)


@timecall
def get_history_time_fast():
    end_time = get_now_seconds_utc()
    start_time = end_time - POLL_PERIOD_SECONDS
    processor = ConnectionPool()

    trade_history = get_history_speedup(start_time, end_time, processor)
    return trade_history


@timecall
def get_order_book_time_fast():
    end_time = get_now_seconds_utc()
    processor = ConnectionPool()
    order_book = get_order_book_speedup(end_time, processor)
    return order_book


def test_open_orders_retrieval_arbitrage():

    sell_exchange_id = EXCHANGE.BINANCE
    buy_exchange_id = EXCHANGE.POLONIEX
    pair_id = CURRENCY_PAIR.BTC_TO_OMG
    threshold = 2.0
    reverse_threshold = 2.0
    balance_threshold = 5.0
    deal_expire_timeout = 60
    logging_level = LOG_ALL_DEBUG

    cfg = ArbitrageConfig(sell_exchange_id, buy_exchange_id,
                          pair_id, threshold,
                          reverse_threshold, balance_threshold,
                          deal_expire_timeout,
                          logging_level)
    load_keys(API_KEY_PATH)
    processor = ConnectionPool(pool_size=2)
    print cfg
    res = get_open_orders_for_arbitrage_pair(cfg, processor)
    print "Length:", len(res)
    for r in res:
        print r
