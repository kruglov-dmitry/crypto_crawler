from profilehooks import timecall

from utils.time_utils import get_now_seconds_utc

from data_access.classes.connection_pool import ConnectionPool

from dao.history_utils import get_history_speedup
from dao.ohlc_utils import get_ohlc_speedup, get_ohlc
from dao.order_book_utils import get_order_book_speedup
from dao.ticker_utils import get_ticker_speedup


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
