#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.base_analysis import compare_price, check_highest_bid_bigger_than_lowest_ask

from dao.ticker_utils import get_ticker_speedup
from dao.db import init_pg_connection, load_to_postgres

from data.Ticker import TICKER_TYPE_NAME
from utils.time_utils import sleep_for, get_now_seconds_utc

from data_access.telegram_notifications import inform_big_boss
from data_access.ConnectionPool import ConnectionPool

# time to poll
POLL_PERIOD_SECONDS = 120
TRIGGER_THRESHOLD = 1.5 # 2 percents only


def analyse_tickers():
    pg_conn = init_pg_connection()

    processor = ConnectionPool()

    while True:

        # tickers = get_ticker()

        timest = get_now_seconds_utc()
        tickers = get_ticker_speedup(timest, processor)

        res = compare_price(tickers, TRIGGER_THRESHOLD, check_highest_bid_bigger_than_lowest_ask)

        if res:
            inform_big_boss(res, pg_conn, POLL_PERIOD_SECONDS)

        all_tickers = []
        for exchange_id in tickers:
            all_tickers += tickers[exchange_id].values()

        print "Total amount of tickers = {num}".format(num = len(all_tickers))
        load_to_postgres(all_tickers, TICKER_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    # FIXME NOTE: read settings from cfg
    # FIXME NOTE 2: some time it hangs at socket read, anti ddos?
    analyse_tickers()
