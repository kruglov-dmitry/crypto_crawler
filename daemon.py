#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram

from core.base_analysis import compare_price, get_diff_lowest_ask_vs_highest_bid, \
    check_highest_bid_bigger_than_lowest_ask
from dao.dao import get_ticker
from data.Ticker import TICKER_TYPE_NAME
from utils.currency_utils import get_pair_name_by_id
from dao.db import init_pg_connection, load_to_postgres, save_alarm_into_pg
from utils.time_utils import sleep_for

# time to poll
POLL_PERIOD_SECONDS = 120
TRIGGER_THRESHOLD = 1.5 # 2 percents only


def inform_big_boss(info_to_report, pg_conn):
    bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')
    print "SEND NOTIFY"
    for debug in info_to_report:
        save_alarm_into_pg(debug[2], debug[3], pg_conn)
        msg = "Condition: {msg} \nPair: {pair_name}, {ask_exchange}: {ask_price} {sell_exchange}: {sell_price}".format(
            msg=debug[0],
            pair_name=get_pair_name_by_id(debug[1]), ask_exchange=debug[2].exchange, ask_price=debug[2].bid,
            sell_exchange=debug[3].exchange, sell_price=debug[3].ask)
        try:
            bot.send_message(chat_id=-218431137, text=str(msg), parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception, e:
            # FIXME still can die
            print "inform_big_boss: ", str(e)
            sleep_for(POLL_PERIOD_SECONDS)
            bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')
            bot.send_message(chat_id=-218431137,
                             text=str(msg),
                             parse_mode=telegram.ParseMode.MARKDOWN)


def analyse_tickers():
    pg_conn = init_pg_connection()

    while True:
        all_tickers = get_ticker()  # return bittrex_tickers, kraken_tickers, poloniex_tickers

        bittrex_tickers = all_tickers[0]
        kraken_tickers = all_tickers[1]
        poloniex_tickers = all_tickers[2]

        res = compare_price(bittrex_tickers, kraken_tickers, poloniex_tickers, TRIGGER_THRESHOLD,
                            get_diff_lowest_ask_vs_highest_bid)

        if res:
            for debug in res:
                save_alarm_into_pg(debug[2], debug[3], pg_conn)
                # inform_big_boss(res, pg_conn)

        res = compare_price(bittrex_tickers, kraken_tickers, poloniex_tickers, TRIGGER_THRESHOLD,
                            check_highest_bid_bigger_than_lowest_ask)

        if res:
            inform_big_boss(res, pg_conn)

        all_tickers = bittrex_tickers.values() + kraken_tickers.values() + poloniex_tickers.values()

        print "Total amount of tickers = {num}".format(num = len(all_tickers))
        load_to_postgres(all_tickers, TICKER_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    # FIXME NOTE: read settings from cfg
    # FIXME NOTE 2: some time it hangs at socket read, anti ddos?
    analyse_tickers()
