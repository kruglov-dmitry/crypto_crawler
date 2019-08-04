from utils.file_utils import log_to_file
from utils.string_utils import float_to_str
from utils.exchange_utils import get_exchange_name_by_id
from debug_utils import print_to_console, LOG_ALL_ERRORS, EXPIRED_ORDER_PROCESSING_FILE_NAME,\
    ERROR_LOG_FILE_NAME, FAILED_ORDER_PROCESSING_FILE_NAME
from data_access.message_queue import DEAL_INFO_MSG, DEBUG_INFO_MSG


def log_cant_cancel_deal(every_deal, msg_queue, log_file_name=EXPIRED_ORDER_PROCESSING_FILE_NAME):
    msg = "CAN'T cancel deal - {deal}".format(deal=every_deal)
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    if log_file_name != EXPIRED_ORDER_PROCESSING_FILE_NAME:
        log_to_file(msg, log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_expired_order_replacement_result(expired_order, json_document, msg_queue):
    msg = """We have tried to replace existing order with new one:
                {o}
                and got response:
                {r}
                """.format(o=expired_order, r=json_document)
    msg_queue.add_message(DEBUG_INFO_MSG, msg)
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_failed_order_replacement_result(failed_order, json_document, msg_queue):
    msg = """We have tried to replace failed order with new one:
                {o}
                and got response:
                {r}
                """.format(o=failed_order, r=json_document)
    msg_queue.add_message(DEBUG_INFO_MSG, msg)
    log_to_file(msg, FAILED_ORDER_PROCESSING_FILE_NAME)


def log_placing_new_deal(every_deal, msg_queue, log_file_name=EXPIRED_ORDER_PROCESSING_FILE_NAME):
    msg = """ We try to send following order to exchange as replacement for expired or failed order.
    Order details: {deal}""".format(deal=str(every_deal))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)

    if log_file_name != EXPIRED_ORDER_PROCESSING_FILE_NAME:
        log_to_file(msg, log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_cant_placing_new_deal(every_deal, msg_queue, log_file_name=EXPIRED_ORDER_PROCESSING_FILE_NAME):
    msg = """   We <b> !!! FAILED !!! </b>
    to send following order to exchange as replacement for expired or failed order.
    Order details:
    {deal}
    """.format(deal=str(every_deal))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    if log_file_name != EXPIRED_ORDER_PROCESSING_FILE_NAME:
        log_to_file(msg, log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_cant_retrieve_order_book(order, msg_queue, log_file_name=EXPIRED_ORDER_PROCESSING_FILE_NAME):
    msg = """ Can't retrieve order book for deal with expired or failed orders!
        Order details: {deal}""".format(deal=str(order))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    if log_file_name != EXPIRED_ORDER_PROCESSING_FILE_NAME:
        log_to_file(msg, log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_cant_retrieve_ticker(order, msg_queue, log_file_name=EXPIRED_ORDER_PROCESSING_FILE_NAME):
    msg = """ Can't retrieve ticker for expired or failed orders!
                Will try to re-process it later.
            Order details: {deal}""".format(deal=str(order))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    if log_file_name != EXPIRED_ORDER_PROCESSING_FILE_NAME:
        log_to_file(msg, log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_dont_have_open_orders(cfg):
    msg = "process_expired_deals - list of open orders from both exchanges is empty, " \
          "REMOVING all watched deals - consider them closed!"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_open_orders_bad_result(cfg):
    msg = "Detected NONE at open_orders - we have to skip this cycle of iteration"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)

    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_open_orders_by_exchange_bad_result(order):
    msg = "Cant retrieve open orders for analysis expired order: {o}".format(o=order)
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_open_orders_is_empty(order):
    msg = """Empty list of open orders for analysis expired order: {o}
    Consider it as FILLED and forgeting it.
    """.format(o=order)
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_balance_expired(exchange_id, threshold, balance_state, msg_queue):
    msg = """<b> !!! CRITICAL !!! </b>
    Balance is OUTDATED for {exch1} for more than {tt} seconds
    Expired or failed orders service will be stopped just in case.
    """.format(exch1=get_exchange_name_by_id(exchange_id), tt=threshold)
    print_to_console(msg, LOG_ALL_ERRORS)
    msg_queue.add_message(DEAL_INFO_MSG, msg)

    log_to_file(msg, ERROR_LOG_FILE_NAME)
    log_to_file(balance_state, ERROR_LOG_FILE_NAME)


def log_too_small_volume(order, max_volume, min_volume, msg_queue):
    msg = """<b> !!! NOT ENOUGH VOLUME !!! </b>
        Balance is not enough to place order
        {o}
        Determined volume is: {v}
        Minimum volume from recent tickers: {mv}
        so we going to ABANDON and FORGET about this order.
        """.format(o=order, v=float_to_str(max_volume), mv=float_to_str(min_volume))
    print_to_console(msg, LOG_ALL_ERRORS)
    msg_queue.add_message(DEAL_INFO_MSG, msg)

    log_to_file(msg, ERROR_LOG_FILE_NAME)

#
#   Methods for verbose debug
#


def log_trace_all_open_orders(open_orders_at_both_exchanges):
    log_to_file("Open orders below:", EXPIRED_ORDER_PROCESSING_FILE_NAME)
    for open_order in open_orders_at_both_exchanges:
        log_to_file(open_order, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_trace_log_time_key(time_key):
    msg = "process_expired_orders - for time key - {tk}".format(tk=str(time_key))
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_trace_log_all_cached_orders_for_time_key(list_of_orders, ts):
    log_to_file("For key {ts} in cached orders - {num} orders".format(ts=ts, num=len(list_of_orders[ts])),
                "expire_deal.log")
    for order in list_of_orders[ts]:
        log_to_file(str(order), EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_trace_order_not_yet_expired(time_key, ts):
    msg = "Too early for processing this key: {kkk} but ts={ts}".format(kkk=time_key, ts=ts)
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_trace_processing_oder(some_order):
    msg = "Check order from watch list - {pair}".format(pair=str(some_order))
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_trace_cancel_request_result(order, err_code, responce):
    msg = "We have tried to send cancel request for order - {dd} and raw result is {er_code} {js}".format(
        dd=str(order), er_code=str(err_code), js=responce)
    log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def log_trace_warched_orders_after_processing(order_list):
    for time_key in order_list:
        msg = "For ts = {ts} cached orders are:".format(ts=str(time_key))
        log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)
        for expired_order in order_list[time_key]:
            log_to_file(str(expired_order), EXPIRED_ORDER_PROCESSING_FILE_NAME)
