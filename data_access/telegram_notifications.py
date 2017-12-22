#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram

from utils.time_utils import sleep_for
from utils.currency_utils import get_pair_name_by_id
from debug_utils import print_to_console, LOG_ALL_DEBUG, LOG_ALL_ERRORS
from utils.string_utils import float_to_str
from utils.file_utils import log_to_file

from dao.db import save_alarm_into_pg

from enums.status import STATUS
from enums.notifications import NOTIFICATION


bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')


def get_chat_id_by_type(notification_id):
    return {
        NOTIFICATION.ARBITRAGE: -218431137,
        NOTIFICATION.DEBUG: -299464102,
        NOTIFICATION.DEAL: -250154235
    }[notification_id]


def inform_big_boss(info_to_report, pg_conn, error_timeout):
    print_to_console("SEND NOTIFY", LOG_ALL_DEBUG)
    for debug in info_to_report:
        save_alarm_into_pg(debug[2], debug[3], pg_conn)
        msg = """Condition: {msg}
        Pair: {pair_name}, {ask_exchange}: {ask_price} {sell_exchange}: {sell_price}
        TAG: {ask_exchange}-{sell_exchange}
        """.format(
            msg=debug[0],
            pair_name=get_pair_name_by_id(debug[1]),
            ask_exchange=debug[2].exchange, ask_price=float_to_str(debug[2].bid),
            sell_exchange=debug[3].exchange, sell_price=float_to_str(debug[3].ask))

        error_code = send_single_message(msg, NOTIFICATION.ARBITRAGE)

        if STATUS.SUCCESS != error_code:
            err_msg = "inform_big_boss can't send message to telegram. Lets try one more time after timeout: {r}".format(r=msg)
            log_to_file(err_msg, "telegram.log")
            print_to_console(err_msg, err_msg)
            sleep_for(error_timeout)
            send_single_message(msg, NOTIFICATION.ARBITRAGE)


def send_single_message(some_message, notification_type):
    global bot
    chat_id = get_chat_id_by_type(notification_type)
    res = STATUS.FAILURE
    try:
        bot.send_message(chat_id=chat_id, text=str(some_message), parse_mode=telegram.ParseMode.HTML)
        res = STATUS.SUCCESS
    except Exception, e:
        msg = "send_single_message FAILED: {msg} {ee}".format(msg=some_message, ee=str(e))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "telegram.log")

    return res
