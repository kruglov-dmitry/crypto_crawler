from dao.db import init_pg_connection, load_to_postgres
from dao.order_book_utils import get_order_book_speedup
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from data_access.classes.ConnectionPool import ConnectionPool
from debug_utils import should_print_debug, print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc, sleep_for

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 5

if __name__ == "__main__":

    pg_conn = init_pg_connection()

    processor = ConnectionPool()

    while True:
        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_PERIOD_SECONDS

        order_book = get_order_book_speedup(start_time, end_time, processor)

        order_book_size = 0
        order_book_ask_size = 0
        order_book_bid_size = 0

        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        order_book_size = len(order_book)

        for entry in order_book:
            if entry is not None:
                order_book_ask_size += len(entry.ask)
                order_book_bid_size += len(entry.bid)

        if should_print_debug():
            msg = """Orderbook retrieval at {tt}:
            Order book size - {num1} Order book asks - {num10} Order book bids - {num20}""".format(
                tt=end_time, num1=order_book_size, num10=order_book_ask_size, num20=order_book_bid_size)
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "order_book.log")

        print_to_console("Before sleep...", LOG_ALL_ERRORS)
        sleep_for(POLL_PERIOD_SECONDS)
