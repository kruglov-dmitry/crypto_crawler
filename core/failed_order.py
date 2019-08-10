from dao.order_book_utils import get_order_book, is_order_book_expired
from dao.ticker_utils import get_ticker
from dao.balance_utils import update_balance_by_exchange
from dao.order_utils import get_open_orders_by_exchange
from dao.order_history_utils import get_order_history_by_exchange
from dao.db import update_order_details

from core.arbitrage_core import adjust_price_by_order_book, compute_min_cap_from_ticker, \
    place_order_by_market_rate

from data_access.message_queue import FAILED_ORDERS_MSG
from data_access.priority_queue import ORDERS_EXPIRE_MSG

from enums.deal_type import DEAL_TYPE
from enums.status import STATUS

from constants import BALANCE_EXPIRED_THRESHOLD
from utils.debug_utils import FAILED_ORDER_PROCESSING_FILE_NAME
from utils.time_utils import sleep_for

from logging_tools.expired_order_logging import log_open_orders_by_exchange_bad_result, log_trace_all_open_orders, \
    log_cant_retrieve_order_book, log_balance_expired, log_cant_retrieve_ticker

from logging_tools.failed_order_logging import log_trace_found_failed_order_in_open, \
    log_trace_found_failed_order_in_history, log_trace_all_closed_orders


def process_failed_order(failed_order, msg_queue, priority_queue, local_cache, pg_conn):
    """

    :param failed_order:
    :param msg_queue:       for notification and orders storage in PG
    :param priority_queue:  maintain list of sucessfuly placed orders ordered by time
    :param local_cache:     cache that contains the most recent balance per exchange
    :param pg_conn:
    :return:

    """

    err_code = search_in_open_orders(failed_order)
    while err_code == STATUS.FAILURE:
        sleep_for(1)
        err_code = search_in_open_orders(failed_order)

    if failed_order.order_id is not None:

        log_trace_found_failed_order_in_open(failed_order)

        update_order_details(pg_conn, failed_order)
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, failed_order)
        return

    err_code = search_in_order_history(failed_order)
    while err_code == STATUS.FAILURE:
        sleep_for(1)
        err_code = search_in_order_history(failed_order)

    if failed_order.order_id is not None:
        log_trace_found_failed_order_in_history(failed_order)

        update_order_details(pg_conn, failed_order)

        return

    # If we are still here it mean that exchange have no glue that we try to place order
    # Supposedly paired order were placed properly so we just place with market rate
    # According to common rules for expired & arbitrage order processing

    ticker = get_ticker(failed_order.exchange_id, failed_order.pair_id)

    if ticker is None:
        msg_queue.add_order(FAILED_ORDERS_MSG, failed_order)

        log_cant_retrieve_ticker(failed_order, msg_queue, log_file_name=FAILED_ORDER_PROCESSING_FILE_NAME)
        return

    min_volume = compute_min_cap_from_ticker(failed_order.pair_id, ticker)
    order_book = get_order_book(failed_order.exchange_id, failed_order.pair_id)

    if order_book is None:
        msg_queue.add_order(FAILED_ORDERS_MSG, failed_order)

        log_cant_retrieve_order_book(failed_order, msg_queue, log_file_name=FAILED_ORDER_PROCESSING_FILE_NAME)

        return

    if is_order_book_expired(FAILED_ORDER_PROCESSING_FILE_NAME, order_book, local_cache, msg_queue):

        msg_queue.add_order(FAILED_ORDERS_MSG, failed_order)

        return

    orders = order_book.bid if failed_order.trade_type == DEAL_TYPE.SELL else order_book.ask

    failed_order.price = adjust_price_by_order_book(orders, failed_order.volume)

    # Forcefully update balance for exchange - maybe other processes consume those coins
    update_balance_by_exchange(failed_order.exchange_id)
    # Do we have enough coins at our balance
    balance = local_cache.get_balance(failed_order.exchange_id)

    if balance.expired(BALANCE_EXPIRED_THRESHOLD):
        msg_queue.add_order(FAILED_ORDERS_MSG, failed_order)

        log_balance_expired(failed_order.exchange_id, BALANCE_EXPIRED_THRESHOLD, balance, msg_queue)

        assert False

    place_order_by_market_rate(failed_order, msg_queue, priority_queue, min_volume, balance,
                               order_book, FAILED_ORDER_PROCESSING_FILE_NAME)


def try_to_set_order_id(open_orders, order):

    print "Compare ", order
    for every_order in open_orders:
        print every_order
        if order.pair_id == every_order.pair_id and order.trade_type == every_order.trade_type and \
                order.price == every_order.price and every_order.create_time >= order.create_time and \
                abs(order.create_time - every_order.create_time) < 15:
            # FIXME
            print "FOUND!!!"
            order.order_id = every_order.order_id
            order.create_time = every_order.create_time


def search_in_open_orders(order):
    status_code, open_orders = get_open_orders_by_exchange(order.exchange_id, order.pair_id)

    if status_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)
        return STATUS.FAILURE

    if not open_orders:
        return STATUS.SUCCESS

    log_trace_all_open_orders(open_orders)

    try_to_set_order_id(open_orders, order)

    return STATUS.SUCCESS


def search_in_order_history(order):
    err_code, closed_orders = get_order_history_by_exchange(order.exchange_id, order.pair_id)

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)
        return STATUS.FAILURE

    if not closed_orders:
        return STATUS.SUCCESS

    log_trace_all_closed_orders(closed_orders)

    try_to_set_order_id(closed_orders, order)

    return STATUS.SUCCESS
