#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import csv

from utils.time_utils import get_now_seconds, sleep_for
import telegram
from dao.dao import get_ohlc, get_ticker, get_history, get_order_book
from core.base_analysis import compare_price
from utils.currency_utils import get_pair_name_by_id
from file_parsing import init_pg_connection, load_to_postgres

from data.Candle import CANDLE_TYPE_NAME
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from data.OrderHistory import TRADE_HISTORY_TYPE_NAME
from data.Ticker import TICKER_TYPE_NAME

DEBUG_ENABLED = True

def should_print_debug():
    return DEBUG_ENABLED

# time to poll
POLL_PERIOD_SECONDS = 120
TRIGGER_THRESHOLD = 1.5 # 2 percents only


def save_to_file(some_data, file_name):
    with open(file_name, "a") as myfile:
        for entry in some_data:
            myfile.write("%s\n" % str(entry))


def inform_big_boss(info_to_report):
    bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')
    print "SEND NOTIFY"
    for debug in info_to_report:
        msg = "Pair: {pair_name}, {ask_exchange}: {ask_price} {sell_exchange}: {sell_price}".format(
            pair_name=get_pair_name_by_id(debug[0]), ask_exchange=debug[1].exchange, ask_price=debug[1].ask, 
            	sell_exchange=debug[2].exchange, sell_price=debug[2].bid)
        try:
            bot.send_message(chat_id=-218431137,
                         text=str(msg),
                         parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception, e:
            # FIXME still can die
            print "inform_big_boss: ", str(e)
            sleep_for(POLL_PERIOD_SECONDS)
            bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')
            bot.send_message(chat_id=-218431137,
                         text=str(msg),
                         parse_mode=telegram.ParseMode.MARKDOWN)


def sock_data():
    pg_conn = init_pg_connection()

    while(True):
        #
        #   First, we grab tickers only to trigger alerts if any
        #

        now_time = get_now_seconds()
        prev_time = now_time - 60

        all_tickers = get_ticker()  # return bittrex_tickers, kraken_tickers, poloniex_tickers

        bittrex_tickers = all_tickers[0]
        kraken_tickers = all_tickers[1]
        poloniex_tickers = all_tickers[2]

        res = compare_price(bittrex_tickers, kraken_tickers, poloniex_tickers, TRIGGER_THRESHOLD)

        if res:
            inform_big_boss(res)

        #
        #   Second, we sock all other data for possible analysis
        #
        all_tickers = bittrex_tickers.values() + kraken_tickers.values() + poloniex_tickers.values()

        candles = get_ohlc()
        order_book = get_order_book()
        trade_history = get_history(prev_time, now_time)

        load_to_postgres(all_tickers, TICKER_TYPE_NAME, pg_conn)
        load_to_postgres(candles, CANDLE_TYPE_NAME, pg_conn)
        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)
        load_to_postgres(trade_history, TRADE_HISTORY_TYPE_NAME, pg_conn)

        """save_to_file(all_tickers, "ticker.txt")
        save_to_file(candles, "ohlc.txt")
        save_to_file(order_book, "order_book.txt")
        save_to_file(trade_history, "trade_history.txt")
        """
        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    # FIXME NOTE: read settings from cfg
    # FIXME NOTE 2: some time it hangs at socket read, anti ddos?
    sock_data()
