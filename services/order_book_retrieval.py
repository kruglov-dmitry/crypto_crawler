import argparse

from dao.db import load_to_postgres
from dao.order_book_utils import get_order_book_speedup

from data.order_book import ORDER_BOOK_TYPE_NAME
from data_access.classes.connection_pool import ConnectionPool

from utils.debug_utils import should_print_debug, print_to_console, LOG_ALL_ERRORS
from constants import ORDER_BOOK_POLL_TIMEOUT

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc, sleep_for

from services.common import process_args


#
#       You can read all data directly using data_retrieval.py
#       But due to throttling pre-cautions from exchanges you may need
#       to start this process at independent node
#


def load_order_books(args):
    """
        Periodically retrieve FULL order books
        from ALL supported exchanges via REST api
        and save it for further analysis in DB.

        Under the hood requests are sent in async fashion via gevent library

    :param args: config file
    :return:
    """

    pg_conn, _ = process_args(args)

    processor = ConnectionPool()

    while True:
        ts = get_now_seconds_utc()

        results = get_order_book_speedup(ts, processor)

        order_book = filter(lambda x: type(x) != str, results)

        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        order_book_size = len(order_book)
        order_book_ask_size = 0
        order_book_bid_size = 0

        for entry in order_book:
            if entry is not None:
                order_book_ask_size += len(entry.ask)
                order_book_bid_size += len(entry.bid)

        if should_print_debug():
            msg = """Orderbook retrieval at {tt}:
            Order book size - {num1} Order book asks - {num10} Order book bids - {num20}""".format(
                tt=ts, num1=order_book_size, num10=order_book_ask_size, num20=order_book_bid_size)
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "order_book.log")

        print_to_console("Before sleep...", LOG_ALL_ERRORS)
        sleep_for(ORDER_BOOK_POLL_TIMEOUT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
      Order book retrieval service - every {tm} retrieve current state of order book from all available exchanges.
          """.format(tm=ORDER_BOOK_POLL_TIMEOUT))

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    load_order_books(arguments)
