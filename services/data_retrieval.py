import argparse

from dao.db import bulk_insert_to_postgres

from dao.history_utils import get_history_speedup
from dao.ohlc_utils import get_ohlc_speedup
from dao.order_book_utils import get_order_book_speedup
from dao.ticker_utils import get_ticker_speedup

from data.candle import Candle
from data.trade_history import TradeHistory
from data.ticker import Ticker
from data.order_book import OrderBook

from data_access.classes.connection_pool import ConnectionPool

from utils.debug_utils import should_print_debug, print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc, sleep_for

from services.common import process_args

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 900


def load_all_public_data(args):
    """
                06.08.2019 As far as I remember it is NOT main data retrieval routine

                Retrieve ticker, trade history, candles and order book
                from ALL supported exchanges
                and store it within DB
                every TIMEOUT seconds through REST api.

                Majority of exchanges tend to throttle clients who send too many requests
                from the same ip - so be mindful about timeout.

    :param args:
    :return:
    """

    pg_conn, settings = process_args(args)

    processor = ConnectionPool()

    def split_on_errors(raw_response):
        valid_objects = filter(lambda x: type(x) != str, raw_response)
        error_strings = filter(lambda x: type(x) != str, raw_response)

        return valid_objects, error_strings

    while True:
        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_PERIOD_SECONDS

        candles, errs = split_on_errors(get_ohlc_speedup(start_time, end_time, processor))
        trade_history, errs = split_on_errors(get_history_speedup(start_time, end_time, processor))
        tickers, errs = split_on_errors(get_ticker_speedup(end_time, processor))
        # order_books, errs = split_on_errors(get_order_book_speedup(end_time, processor))

        bulk_insert_to_postgres(pg_conn, Candle.table_name, Candle.columns, candles)
        bulk_insert_to_postgres(pg_conn, TradeHistory.table_name, TradeHistory.columns, trade_history)
        bulk_insert_to_postgres(pg_conn, Ticker.table_name, Ticker.columns, tickers)

        # bulk_insert_to_postgres(pg_conn, OrderBook.table_name, OrderBook.columns, order_books)

        if should_print_debug():
            msg = """History retrieval at {ts}:
                Candle size - {num}
                Ticker size - {num3}
                Trade history size - {num2}
                """.format(ts=end_time, num=len(candles), num3=len(tickers), num2=len(trade_history))
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "candles_trade_history.log")

        print_to_console("Before sleep...", LOG_ALL_ERRORS)
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
    Data retrieval service - every {tm} retrieve trades history, tickers and candles 
    from all available exchanges.
        """.format(tm=POLL_PERIOD_SECONDS))

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    load_all_public_data(arguments)
