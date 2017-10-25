from dao.dao import get_ohlc, get_history, get_order_book
from data.Candle import CANDLE_TYPE_NAME
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from data.OrderHistory import TRADE_HISTORY_TYPE_NAME
from debug_utils import should_print_debug
from dao.db import init_pg_connection, load_to_postgres
from utils.time_utils import get_now_seconds, sleep_for

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 900

if __name__ == "__main__":

    pg_conn = init_pg_connection()

    while True:
        #
        #   First, we grab tickers only to trigger alerts if any
        #

        now_time = get_now_seconds()
        prev_time = now_time - POLL_PERIOD_SECONDS
        candles = get_ohlc()
        order_book = get_order_book()
        trade_history = get_history(prev_time, now_time)

        if should_print_debug():
            print "Candle size - {num} \nOrder book size - {num1} \nTrade history size - {num2}".format(
                num=len(candles), num1=len(order_book), num2=len(trade_history))

        load_to_postgres(candles, CANDLE_TYPE_NAME, pg_conn)
        load_to_postgres(order_book.values(), ORDER_BOOK_TYPE_NAME, pg_conn)
        load_to_postgres(trade_history, TRADE_HISTORY_TYPE_NAME, pg_conn)

        """save_to_file(all_tickers, "ticker.txt")
        save_to_file(candles, "ohlc.txt")
        save_to_file(order_book, "order_book.txt")
        save_to_file(trade_history, "trade_history.txt")
        """

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)

