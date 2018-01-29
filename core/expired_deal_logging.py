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


def log_cant_retrieve_order_book(every_deal, cfg, msg_queue):
    msg = """ Can't retrieve order book for deal with expired orders!
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


#
#   Methods for verbose debug
#

def log_trace_all_open_orders(open_orders_at_both_exchanges):
    log_to_file("Open orders below:", "expire_deal.log")
    for v in open_orders_at_both_exchanges:
        log_to_file(v, "expire_deal.log")


def log_trace_log_time_key(time_key):
    msg = "process_expired_orders - for time key - {tk}".format(tk=str(time_key))
    log_to_file(msg, "expire_deal.log")


def log_trace_log_all_cached_orders_for_time_key(list_of_orders, ts):
    log_to_file("For key {ts} in cached orders - {num} orders".format(ts=ts, num=len(list_of_orders[ts])),
                "expire_deal.log")
    for order in list_of_orders[ts]:
        log_to_file(str(order), "expire_deal.log")


def log_trace_order_not_yet_expired(time_key, ts):
    msg = "Too early for processing this key: {kkk} but ts={ts}".format(kkk=time_key, ts=ts)
    log_to_file(msg, "expire_deal.log")


def log_trace_processing_oder(some_order):
    msg = "Check order from watch list - {pair}".format(pair=str(some_order))
    log_to_file(msg, "expire_deal.log")


def log_trace_cancel_request_result(order, err_code, responce):
    msg = "We have tried to send cancel request for order - {dd} and raw result is {er_code} {js}".format(
        dd=str(order), er_code=str(err_code), js=responce)
    log_to_file(msg, "expire_deal.log")


def log_trace_warched_orders_after_processing(order_list):
    for tkey in order_list:
        msg = "For ts = {ts} cached orders are:".format(ts=str(tkey))
        log_to_file(msg, "expire_deal.log")
        for b in order_list[tkey]:
            log_to_file(str(b), "expire_deal.log")