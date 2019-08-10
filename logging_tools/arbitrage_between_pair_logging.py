from utils.debug_utils import LOG_ALL_ERRORS, print_to_console, SOCKET_ERRORS_LOG_FILE_NAME, \
    CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME

from utils.file_utils import log_to_file
from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.time_utils import ts_to_string_utc

from data_access.message_queue import DEAL_INFO_MSG
from constants import BALANCE_EXPIRED_THRESHOLD

from services.sync_stage import get_stage


def log_balance_expired_errors(cfg, msg_queue, balance_state):
    msg = """<b> !!! CRITICAL !!! </b>
    Balance is OUTDATED for {exch1} or {exch2} for more than {tt} seconds
    Arbitrage process will be stopped just in case.
    Check log file: {lf}""".format(exch1=get_exchange_name_by_id(cfg.buy_exchange_id),
                                   exch2=get_exchange_name_by_id(cfg.sell_exchange_id),
                                   tt=BALANCE_EXPIRED_THRESHOLD, lf=cfg.log_file_name)
    print_to_console(msg, LOG_ALL_ERRORS)
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    log_to_file(msg, cfg.log_file_name)
    log_to_file(balance_state, cfg.log_file_name)


def log_failed_to_retrieve_order_book(cfg):
    msg = "CAN'T retrieve order book for {nn} or {nnn}".format(nn=get_exchange_name_by_id(cfg.sell_exchange_id),
                                                               nnn=get_exchange_name_by_id(cfg.buy_exchange_id))
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)


def log_dont_supported_currency(cfg, exchange_id, pair_id):
    msg = "Not supported currency {idx}-{name} for {exch}".format(idx=cfg.pair_id, name=pair_id,
                                                                  exch=get_exchange_name_by_id(exchange_id))
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)


def log_dublicative_order_book(log_file_name, msg_queue, order_book, prev_order_book):
    msg = """ <b> !!! WARNING !!! </b>
    Number of similar asks OR bids are the same for the most recent and cached version of order book for
    exchange_name {exch} pair_name {pn}
    cached timest: {ts1} {dt1}
    recent timest: {ts2} {dt2}
    Verbose information can be found in logs error & 
    """.format(exch=get_exchange_name_by_id(order_book.exchange_id),
               pn=get_currency_pair_name_by_exchange_id(order_book.pair_id, order_book.exchange_id),
               ts1=prev_order_book.timest, dt1=ts_to_string_utc(prev_order_book.timest), ts2=order_book.timest,
               dt2=ts_to_string_utc(order_book.timest))

    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, log_file_name)

    msg = """Cached version of order book: 
    {o}
    Recent version of order book:
    {oo}
    """.format(o=str(prev_order_book), oo=str(order_book))
    log_to_file(msg, log_file_name)


#
#   08.03.2019 simplification of websocket based subscription code
#


def log_init_reset():
    msg = "reset_arbitrage_state: started"
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_reset_final_stage():
    msg = "reset_arbitrage_state invoked: before final stage check"
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_reset_stage_successfully():
    msg = "reset_arbitrage_state - success!"
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_cant_update_volume_cap(pair_id, buy_exchange_id, sell_exchange_id, log_file_name):
    msg = """CAN'T update minimum_volume_cap for {pair_id} at following exchanges: {exch1} {exch2}""".format(
        pair_id=pair_id, exch1=get_exchange_name_by_id(buy_exchange_id),
        exch2=get_exchange_name_by_id(sell_exchange_id))

    log_to_file(msg, log_file_name)
    log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)

    print_to_console(msg, LOG_ALL_ERRORS)


def log_finishing_syncing_order_book(kind):
    msg = "Finishing syncing {kind} order book!".format(kind=kind)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_all_order_book_synced():
    msg = "sync_order_books - AFTER MAIN LOOP - stage status is {}".format(get_stage())
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_order_book_update_failed_pre_sync(kind, exchange_id, order_book_updates):
    msg = "Reset stage will be initiated because Orderbook update FAILED during pre-SYNC stage - {kind} - " \
          "for {exch_name} Update itself: {upd}".format(kind=kind,
                                                        exch_name=get_exchange_name_by_id(exchange_id),
                                                        upd=order_book_updates)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_order_book_update_failed_post_sync(exchange_id, order_book_updates):
    msg = "Update after syncing FAILED = Order book update is FAILED! for {exch_name} Update itself: {upd}".format(
        exch_name=get_exchange_name_by_id(exchange_id), upd=order_book_updates)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    print_to_console(msg, LOG_ALL_ERRORS)


def log_one_of_subscriptions_failed(buy_subscription, sell_subscription, curent_stage):
    msg = "One of processes stopped: buy: {b_s} sell: {s_s} current stage is {st}".format(
        b_s=buy_subscription, s_s=sell_subscription, st=curent_stage)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)
