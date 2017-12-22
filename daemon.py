#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.base_analysis import compare_price, check_highest_bid_bigger_than_lowest_ask

from dao.ticker_utils import get_ticker_speedup
from dao.db import init_pg_connection, load_to_postgres

from data.Ticker import TICKER_TYPE_NAME
from utils.time_utils import sleep_for, get_now_seconds_utc

from data_access.telegram_notifications import inform_big_boss
from data_access.ConnectionPool import ConnectionPool

from debug_utils import print_to_console, LOG_ALL_DEBUG

# time to poll
POLL_PERIOD_SECONDS = 120
TRIGGER_THRESHOLD = 1.5 # 2 percents only


def analyse_tickers():
    pg_conn = init_pg_connection()

    processor = ConnectionPool()

    while True:

        timest = get_now_seconds_utc()
        tickers = get_ticker_speedup(timest, processor)

        res = compare_price(tickers, TRIGGER_THRESHOLD, check_highest_bid_bigger_than_lowest_ask)

        if res:
            inform_big_boss(res, pg_conn, POLL_PERIOD_SECONDS)

        print_to_console("Total amount of tickers = {num}".format(num=len(tickers)), LOG_ALL_DEBUG)
        load_to_postgres(tickers, TICKER_TYPE_NAME, pg_conn)

        print_to_console("Before sleep...", LOG_ALL_DEBUG)
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    # FIXME NOTE: read settings from cfg
    analyse_tickers()
