#!/usr/bin/python
# -*- coding: utf-8 -*-

from data_access.message_queue import get_message_queue, ARBITRAGE_MSG

from core.base_analysis import compare_price, check_highest_bid_bigger_than_lowest_ask
from dao.db import init_pg_connection, load_to_postgres, save_alarm_into_pg
from dao.ticker_utils import get_ticker_speedup
from data.Ticker import TICKER_TYPE_NAME
from data_access.classes.ConnectionPool import ConnectionPool
from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_DEBUG
from utils.currency_utils import get_pair_name_by_id
from utils.string_utils import float_to_str
from utils.time_utils import sleep_for, get_now_seconds_utc, ts_to_string
import argparse
from deploy.classes.CommonSettings import CommonSettings


# time to poll
POLL_PERIOD_SECONDS = 120
TRIGGER_THRESHOLD = 1.5 # 2 percents only


def analyse_tickers(pg_conn, msg_queue):

    processor = ConnectionPool()

    while True:

        timest = get_now_seconds_utc()
        tickers = get_ticker_speedup(timest, processor)

        res = compare_price(tickers, TRIGGER_THRESHOLD, check_highest_bid_bigger_than_lowest_ask)

        for entry in res:
            msg = """Condition: {msg} at {ts}
            Date: {dt}
            Pair: {pair_name}, {ask_exchange}: {ask_price} {sell_exchange}: {sell_price}
            TAG: {ask_exchange}-{sell_exchange}
            """.format(msg=entry[0], ts = timest, dt = ts_to_string(timest), pair_name=get_pair_name_by_id(entry[1]),
                       ask_exchange=entry[2].exchange, ask_price=float_to_str(entry[2].bid),
                       sell_exchange=entry[3].exchange, sell_price=float_to_str(entry[3].ask))
            print_to_console(msg, LOG_ALL_ERRORS)

            msg_queue.add_message(ARBITRAGE_MSG, msg)
            save_alarm_into_pg(entry[2], entry[3], pg_conn)

        print_to_console("Total amount of tickers = {num}".format(num=len(tickers)), LOG_ALL_DEBUG)
        load_to_postgres(tickers, TICKER_TYPE_NAME, pg_conn)

        print_to_console("Before sleep...", LOG_ALL_DEBUG)
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Arbitrage monitoring service, every {POLL_TIMEOUT}: 
        - retrieve tickers
        - compare high \ low per pair
        - if difference bigger than {THRES} %
        - trigger notification message
    """.format(POLL_TIMEOUT=POLL_PERIOD_SECONDS, THRES=TRIGGER_THRESHOLD))

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    pg_conn = init_pg_connection(_db_host=settings.db_host,
                                 _db_port=settings.db_port,
                                 _db_name=settings.db_name)

    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)
    analyse_tickers(pg_conn, msg_queue)
