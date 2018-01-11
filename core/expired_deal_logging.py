from utils.file_utils import log_to_file
from debug_utils import print_to_console, LOG_ALL_ERRORS
from data_access.message_queue import DEAL_INFO_MSG


def log_cant_cancel_deal(every_deal, cfg, msg_queue):
    msg = "CAN'T cancel deal - {deal}".format(deal=every_deal)
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, "expire_deal.log")


def log_placing_new_deal(every_deal, cfg, msg_queue):
    msg = """ We try to send following deal to exchange as replacement for expired order.
    Deal details: {deal}""".format(deal=str(every_deal))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, "expire_deal.log")


def log_cant_placing_new_deal(every_deal, cfg, msg_queue):
    msg = """   We <b> !!! FAILED !!! </b>
    to send following deal to exchange as replacement for expired order.
    Deal details:
    {deal}
    """.format(deal=str(every_deal))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, "expire_deal.log")


def log_cant_find_order_book(every_deal, cfg, msg_queue):
    msg = """ Can't find order book for deal with expired orders!
        Order details: {deal}""".format(deal=str(every_deal))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, "expire_deal.log")


def log_dont_have_open_orders(cfg):
    msg = "process_expired_deals - list of open orders from both exchanges is empty, " \
          "REMOVING all watched deals - consider them closed!"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, "expire_deal.log")


def log_open_orders_bad_result(cfg):
    msg = "Detected NONE at open_orders - we have to skip this cycle of iteration"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, "expire_deal.log")