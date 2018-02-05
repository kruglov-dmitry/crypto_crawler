from data_access.message_queue import get_message_queue, FAILED_ORDERS_MSG, ORDERS_MSG
from data_access.priority_queue import ORDERS_EXPIRE_MSG, get_priority_queue

from dao.db import init_pg_connection, update_order_details
from dao.order_utils import get_open_orders_by_exchange
from dao.order_history_utils import get_order_history_by_exchange
from dao.order_book_utils import get_order_book
from dao.deal_utils import init_deal
from dao.dao import parse_deal_id

from core.arbitrage_core import adjust_price_by_order_book
from core.expired_deal_logging import log_open_orders_by_exchange_bad_result, log_trace_all_open_orders, \
    log_cant_retrieve_order_book, log_placing_new_deal, log_cant_placing_new_deal

from debug_utils import print_to_console, LOG_ALL_ERRORS, FAILED_ORDER_PROCESSING_FILE_NAME
from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.file_utils import log_to_file

from enums.status import STATUS
from enums.deal_type import DEAL_TYPE

EXPIRATION_TIMEOUT = 15
HEARTBEAT_TIMEOUT = 60

FLOAT_POINT_PRECISION = 0.00000001


def try_to_set_deal_id(open_orders, order):

    for every_order in open_orders:
        if order.pair_id == every_order.pair_id and \
                        order.deal_type == every_order.deal_type and \
                        abs(order.price - every_order.price) < FLOAT_POINT_PRECISION and \
                        order.create_time >= every_order.create_time and \
                        abs(order.create_time - every_order.create_time) < 15:
            # FIXME
            order.deal_id = every_order.deal_id
            order.create_time = every_order.create_time


def search_in_open_orders(order, msg_queue):
    err_code, open_orders = get_open_orders_by_exchange(order.exchange_id, order.pair_id)

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)
        msg_queue.add_order(FAILED_ORDERS_MSG, order)
        return

    present_in_open_orders = len(open_orders) != 0

    if not present_in_open_orders:
        log_trace_all_open_orders(open_orders)

        try_to_set_deal_id(open_orders, order)


def log_trace_all_closed_orders(open_orders_at_both_exchanges):
    log_to_file("Closed orders below:", FAILED_ORDER_PROCESSING_FILE_NAME)
    for v in open_orders_at_both_exchanges:
        log_to_file(v, FAILED_ORDER_PROCESSING_FILE_NAME)


def search_in_order_history(order, msg_queue):
    err_code, closed_orders = get_order_history_by_exchange(order.exchange_id, order.pair_id)

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)
        msg_queue.add_order(FAILED_ORDERS_MSG, order)
        return

    present_in_old_orders = len(closed_orders) != 0

    if not present_in_old_orders:
        log_trace_all_closed_orders(closed_orders)

        try_to_set_deal_id(closed_orders, order)


if __name__ == "__main__":

    # FIXME NOTE: read from config redis host \ port pass it to get_*_queue methods

    """
                We try to address following issue
                
            Due to network issue or just bugs we may end up in situation that we are failed to place order
                    Or we think so.
                    
            Option 1: We managed to place order, just didn't wait for exchange enough timeout
            Option 2: nonce issue - particular poloniex
            
            Option 3: ??? TODO
            
            First we try to find order in open or executed.
            In case we find it - update deal_id in db.
            If it still open add it to watch list for expired orders processing.
            
            If not we can replace it by market with idea that there is high probability that other arbitrage deal were 
            successfully placed
    """

    # FIXME NOTE - read settings from cfg!

    msg_queue = get_message_queue()
    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")
    priority_queue = get_priority_queue()
    cnt = 0

    while True:
        order = msg_queue.get_next_order(FAILED_ORDERS_MSG)
        if order is not None:

            search_in_open_orders(order, msg_queue)
            if order.deal_id is not None:
                update_order_details(pg_conn, order)
                priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)
                continue
            else:
                search_in_order_history(order, msg_queue)
                if order.deal_id is not None:
                    update_order_details(pg_conn, order)
                    continue

            # If we are still here it mean that exchange have no glue that we try to place order
            # Supposedly paired order were placed properly so we just place with market rate
            order_book = get_order_book(order.exchange_id, order.pair_id)

            if order_book is not None:

                orders = order_book.bid if order.trade_type == DEAL_TYPE.SELL else order_book.ask

                order.price = adjust_price_by_order_book(orders, order.volume)
                order.create_time = get_now_seconds_utc()

                msg = "Replace existing order with new one - {tt}".format(tt=order)
                err_code, json_document = init_deal(order, msg)
                if err_code == STATUS.SUCCESS:

                    order.execute_time = get_now_seconds_utc()
                    order.order_book_time = long(order_book.timest)
                    order.deal_id = parse_deal_id(order.exchange_id, json_document)

                    msg_queue.add_order(ORDERS_MSG, order)

                    priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

                    log_placing_new_deal(order, msg_queue)
                else:
                    log_cant_placing_new_deal(order, msg_queue)

                    msg_queue.add_order(FAILED_ORDERS_MSG, order)
            else:
                log_cant_retrieve_order_book(order, msg_queue)

        sleep_for(1)
        cnt += 1

        if cnt >= 60:
            cnt = 0
            print_to_console("Failed orders processing heartbeat", LOG_ALL_ERRORS)