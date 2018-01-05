#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file

from enums.status import STATUS
from enums.notifications import NOTIFICATION


bot = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')


def get_chat_id_by_type(notification_id):
    return {
        NOTIFICATION.ARBITRAGE: -218431137,
        NOTIFICATION.DEBUG: -299464102,
        NOTIFICATION.DEAL: -250154235
    }[notification_id]


def send_single_message(some_message, notification_type):
    global bot
    chat_id = get_chat_id_by_type(notification_type)
    res = STATUS.FAILURE
    try:
        bot.send_message(chat_id=chat_id, text=str(some_message), timeout=5,
                         parse_mode=telegram.ParseMode.HTML)
        res = STATUS.SUCCESS
    except Exception, e:
        msg = "send_single_message FAILED: {msg} {ee}".format(msg=some_message, ee=str(e))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "telegram.log")

    return res
