#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram

from utils.currency_utils import get_pair_name_by_id
from dao.db import save_alarm_into_pg
from utils.time_utils import sleep_for
from enums.status import STATUS


def inform_big_boss(info_to_report, pg_conn, error_timeout):
    bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')
    print "SEND NOTIFY"
    for debug in info_to_report:
        save_alarm_into_pg(debug[2], debug[3], pg_conn)
        msg = "Condition: {msg} \nPair: {pair_name}, {ask_exchange}: {ask_price} {sell_exchange}: {sell_price}".format(
            msg=debug[0],
            pair_name=get_pair_name_by_id(debug[1]), ask_exchange=debug[2].exchange, ask_price=debug[2].bid,
            sell_exchange=debug[3].exchange, sell_price=debug[3].ask)

        error_code = send_single_message(msg)

        if STATUS.SUCCESS != error_code:
            print "inform_big_boss can't send message to telegram. Lets try one more time after timeout."
            sleep_for(error_timeout)
            send_single_message(msg)


def send_single_message(some_message):
    res = STATUS.FAILURE
    bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')
    try:
        bot.send_message(chat_id=-218431137, text=str(some_message), parse_mode=telegram.ParseMode.MARKDOWN)
        res = STATUS.SUCCESS
    except Exception, e:
        # FIXME still can die
        print "send_single_message: ", str(e)

    return res
