#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram

from utils.debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file

from enums.status import STATUS
from enums.notifications import NOTIFICATION

MAX_MESSAGE_LENGTH = 4000


BOT = telegram.Bot(token='438844686:AAE8lS3VyMsNgtytR4I1uWy4DLUaot2e5hU')


def get_chat_id_by_type(notification_id):
    return {
        NOTIFICATION.ARBITRAGE: -218431137,
        NOTIFICATION.DEBUG: -299464102,
        NOTIFICATION.DEAL: -250154235
    }[notification_id]


def log_error_send_message(func_name, some_message, exception):
    msg = "{func_name} FAILED: {msg} {ee}".format(func_name=func_name, msg=some_message, ee=exception)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, "telegram.log")


def send_single_message_no_parsing(some_message, notification_type):
    chat_id = get_chat_id_by_type(notification_type)
    res = STATUS.FAILURE
    try:
        BOT.send_message(chat_id=chat_id, text=str(some_message), timeout=5, parse_mode=None)
        res = STATUS.SUCCESS
    except Exception as e:
        log_error_send_message("send_single_message_no_parsing", some_message, e)

    return res


def send_single_message(some_message, notification_type):

    if len(some_message) > MAX_MESSAGE_LENGTH:
        some_message = some_message[:MAX_MESSAGE_LENGTH] + "... etc"

    chat_id = get_chat_id_by_type(notification_type)

    try:
        BOT.send_message(chat_id=chat_id, text=str(some_message), timeout=5,
                         parse_mode=telegram.ParseMode.HTML)
        res = STATUS.SUCCESS
    except Exception as e:
        log_error_send_message("send_single_message", some_message, e)
        res = send_single_message_no_parsing(some_message, notification_type)

    return res
