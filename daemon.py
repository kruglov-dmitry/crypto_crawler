#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.base_analysis import compare_price, get_diff_lowest_ask_vs_highest_bid, \
    check_highest_bid_bigger_than_lowest_ask
from dao.dao import get_ticker
from data.Ticker import TICKER_TYPE_NAME
from dao.db import init_pg_connection, load_to_postgres, save_alarm_into_pg
from utils.time_utils import sleep_for
from data_access.telegram_notifications import inform_big_boss

# time to poll
POLL_PERIOD_SECONDS = 120
TRIGGER_THRESHOLD = 1.5 # 2 percents only


def analyse_tickers():
    pg_conn = init_pg_connection()

    while True:
        bittrex_tickers, kraken_tickers, poloniex_tickers, binance_tickers = get_ticker()

        res = compare_price(bittrex_tickers, kraken_tickers, poloniex_tickers, binance_tickers, TRIGGER_THRESHOLD,
                            check_highest_bid_bigger_than_lowest_ask)

        if res:
            inform_big_boss(res, pg_conn, POLL_PERIOD_SECONDS)

        all_tickers = bittrex_tickers.values() + kraken_tickers.values() + poloniex_tickers.values() + binance_tickers.values()

        print "Total amount of tickers = {num}".format(num = len(all_tickers))
        load_to_postgres(all_tickers, TICKER_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    # FIXME NOTE: read settings from cfg
    # FIXME NOTE 2: some time it hangs at socket read, anti ddos?
    analyse_tickers()
