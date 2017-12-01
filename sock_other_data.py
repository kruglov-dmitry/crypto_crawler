from dao.dao import get_ohlc, get_history, get_order_book
from data.Candle import CANDLE_TYPE_NAME
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from data.OrderHistory import TRADE_HISTORY_TYPE_NAME
from debug_utils import should_print_debug
from dao.db import init_pg_connection, load_to_postgres
from utils.time_utils import get_now_seconds_local, get_now_seconds_utc, sleep_for
from utils.file_utils import log_to_file

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 900

if __name__ == "__main__":

    pg_conn = init_pg_connection()

    while True:
        #
        #   First, we grab tickers only to trigger alerts if any
        #

        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_PERIOD_SECONDS

        candles = get_ohlc(start_time, end_time)
        order_book = get_order_book()
        order_book_size = 0
        order_book_ask_size = 0
        order_book_bid_size = 0

        trade_history = get_history(start_time, end_time)

        load_to_postgres(candles, CANDLE_TYPE_NAME, pg_conn)

        for exchange_id in order_book:
            load_to_postgres(order_book[exchange_id], ORDER_BOOK_TYPE_NAME, pg_conn)
        load_to_postgres(trade_history, TRADE_HISTORY_TYPE_NAME, pg_conn)

        for exchange_id in order_book:
            order_book_size += len(order_book[exchange_id])
            for entry in order_book[exchange_id]:
                order_book_ask_size += len(entry.ask)
                order_book_bid_size += len(entry.bid)

        if should_print_debug():
            msg = "Sock other data:\n Candle size - {num} \nOrder book size - {num1} Order book asks - {num10} Order book bids - {num20} \nTrade history size - {num2}".format(
                num=len(candles), num1=order_book_size, num2=len(trade_history), num10=order_book_ask_size, num20=order_book_bid_size)
            print msg
            log_to_file(msg, "sock_other_data.txt")

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)
