from dao.order_book_utils import get_order_book
from dao.ticker_utils import get_ticker
from dao.deal_utils import init_deal
from dao.dao import parse_deal_id

from core.arbitrage_core import adjust_price_by_order_book, compute_min_cap_from_ticker, \
    determine_maximum_volume_by_balance, round_volume

from dao.db import update_order_details

from data_access.message_queue import ORDERS_MSG, FAILED_ORDERS_MSG
from data_access.priority_queue import ORDERS_EXPIRE_MSG

from enums.deal_type import DEAL_TYPE
from enums.status import STATUS

from constants import BALANCE_EXPIRED_THRESHOLD, FLOAT_POINT_PRECISION
from debug_utils import FAILED_ORDER_PROCESSING_FILE_NAME
from utils.time_utils import sleep_for, get_now_seconds_utc

from dao.order_utils import get_open_orders_by_exchange
from dao.order_history_utils import get_order_history_by_exchange

from core.expired_order_logging import log_open_orders_by_exchange_bad_result, log_trace_all_open_orders, \
    log_cant_retrieve_order_book, log_placing_new_deal, log_cant_placing_new_deal, log_balance_expired, \
    log_too_small_volume

from core.failed_order_logging import log_trace_found_failed_order_in_open, log_trace_found_failed_order_in_history, \
    log_trace_all_closed_orders


def process_failed_order(order, msg_queue, priority_queue, local_cache, pg_conn):
    """

    :param order:
    :param msg_queue:       for notification and orders storage in PG
    :param priority_queue:  maintain list of sucessfuly placed orders ordered by time
    :param local_cache:     cache that contains the most recent balance per exchange
    :param pg_conn:
    :return:

    """

    err_code = search_in_open_orders(order)
    while err_code == STATUS.FAILURE:
        sleep_for(1)
        err_code = search_in_open_orders(order)

    if order.deal_id is not None:

        log_trace_found_failed_order_in_open(order)

        update_order_details(pg_conn, order)
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)
        return

    err_code = search_in_order_history(order)
    while err_code == STATUS.FAILURE:
        sleep_for(1)
        err_code = search_in_order_history(order)

    if order.deal_id is not None:
        log_trace_found_failed_order_in_history(order)

        update_order_details(pg_conn, order)
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

        return

    # If we are still here it mean that exchange have no glue that we try to place order
    # Supposedly paired order were placed properly so we just place with market rate
    # According to common rules for expired & arbitrage order processing

    ticker = get_ticker(order.exchange_id, order.pair_id)
    min_volume = compute_min_cap_from_ticker(order.pair_id, ticker)
    order_book = get_order_book(order.exchange_id, order.pair_id)

    if order_book is not None:

        orders = order_book.bid if order.trade_type == DEAL_TYPE.SELL else order_book.ask

        order.price = adjust_price_by_order_book(orders, order.volume)
        # Do we have enough coins at our balance
        balance = local_cache.get_balance(order.exchange_id)

        if balance.expired(BALANCE_EXPIRED_THRESHOLD):
            msg_queue.add_order(FAILED_ORDERS_MSG, order)

            log_balance_expired(order.exchange_id, BALANCE_EXPIRED_THRESHOLD, balance, msg_queue)

            assert False

        max_volume = determine_maximum_volume_by_balance(order.pair_id, order.trade_type,
                                                         order.volume, order.price,
                                                         balance)

        max_volume = round_volume(order.exchange_id, max_volume, order.pair_id)

        if max_volume < min_volume:
            log_too_small_volume(order, max_volume, min_volume, msg_queue)

            return

        order.volume = max_volume
        order.create_time = get_now_seconds_utc()

        msg = "Replace FAILED order with new one - {tt}".format(tt=order)
        err_code, json_document = init_deal(order, msg)
        if err_code == STATUS.SUCCESS:

            order.execute_time = get_now_seconds_utc()
            order.order_book_time = long(order_book.timest)
            order.deal_id = parse_deal_id(order.exchange_id, json_document)

            msg_queue.add_order(ORDERS_MSG, order)

            priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

            log_placing_new_deal(order, msg_queue, log_file_name=FAILED_ORDER_PROCESSING_FILE_NAME)
        else:
            msg_queue.add_order(FAILED_ORDERS_MSG, order)
            log_cant_placing_new_deal(order, msg_queue, log_file_name=FAILED_ORDER_PROCESSING_FILE_NAME)
    else:
        msg_queue.add_order(FAILED_ORDERS_MSG, order)
        log_cant_retrieve_order_book(order, msg_queue, log_file_name=FAILED_ORDER_PROCESSING_FILE_NAME)


def try_to_set_deal_id(open_orders, order):

    print "Compare ", order
    for every_order in open_orders:
        print every_order
        if order.pair_id == every_order.pair_id and \
                        order.trade_type == every_order.trade_type and \
                        abs(order.price - every_order.price) < FLOAT_POINT_PRECISION and \
                        every_order.create_time >= order.create_time and \
                        abs(order.create_time - every_order.create_time) < 15:
            # FIXME
            print "FOUND!!!"
            order.deal_id = every_order.deal_id
            order.create_time = every_order.create_time


def search_in_open_orders(order):
    err_code, open_orders = get_open_orders_by_exchange(order.exchange_id, order.pair_id)

    print "WHYWHYW"
    print err_code
    print open_orders

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)
        return STATUS.FAILURE

    if len(open_orders) == 0:
        return STATUS.SUCCESS

    log_trace_all_open_orders(open_orders)

    try_to_set_deal_id(open_orders, order)

    return STATUS.SUCCESS


def search_in_order_history(order):
    err_code, closed_orders = get_order_history_by_exchange(order.exchange_id, order.pair_id)

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)
        return STATUS.FAILURE

    if len(closed_orders) == 0:
        return STATUS.SUCCESS

    log_trace_all_closed_orders(closed_orders)

    try_to_set_deal_id(closed_orders, order)

    return STATUS.SUCCESS