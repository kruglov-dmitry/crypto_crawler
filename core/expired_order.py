from core.arbitrage_core import adjust_price_by_order_book, determine_maximum_volume_by_balance, \
    compute_min_cap_from_ticker, round_volume
from logging_tools.expired_order_logging import log_cant_cancel_deal, log_placing_new_deal, \
    log_cant_placing_new_deal, log_cant_retrieve_order_book, log_trace_all_open_orders, \
    log_trace_cancel_request_result, log_open_orders_by_exchange_bad_result, log_open_orders_is_empty, \
    log_balance_expired, log_too_small_volume, log_cant_retrieve_ticker

from dao.order_utils import get_open_orders_by_exchange
from dao.ticker_utils import get_ticker
from dao.dao import cancel_by_exchange, parse_order_id
from dao.deal_utils import init_deal
from dao.order_book_utils import get_order_book
from dao.balance_utils import update_balance_by_exchange

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc, sleep_for

from data_access.message_queue import ORDERS_MSG, FAILED_ORDERS_MSG
from data_access.priority_queue import ORDERS_EXPIRE_MSG

from enums.status import STATUS
from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE

from constants import BALANCE_EXPIRED_THRESHOLD


def process_expired_order(order, msg_queue, priority_queue, local_cache):
    """
            In order to speedup and simplify expired deal processing following approach implemented.

            Every successfully placed order go into priority queue sorted by time. Earliest - first.
            When time come - it will appear in this method.
            We retrieve open orders and try to find that order there.
            If it still there:
                adjust executed volume
                cancel active order
                retrieve order book and adjust price
                place new order with new volume and price

            FIXME NOTE: poloniex(? other ?) executed volume = 0 and volume != original ?

    :param order:  order retrieved from redis cache
    :param msg_queue: saving to postgres and re-process failed orders
    :param priority_queue: watch queue for expired orders
    :param local_cache: to retrieve balance
    :return:
    """

    err_code, open_orders = get_open_orders_by_exchange(order.exchange_id, order.pair_id)

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(order)

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

        return

    if len(open_orders) == 0:
        log_open_orders_is_empty(order)
        return

    log_trace_all_open_orders(open_orders)

    if update_executed_volume(open_orders, order):
        err_code, responce = cancel_by_exchange(order)

        log_trace_cancel_request_result(order, err_code, responce)

        if err_code == STATUS.FAILURE:
            log_cant_cancel_deal(order, msg_queue)

            priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

            return

        # FIXME NOTE
        # so we want exchange update for us available balance
        # as we observe situation where its not happen immediatly we want to mitigate delay
        # with this dirty workaround
        sleep_for(2)

        ticker = get_ticker(order.exchange_id, order.pair_id)
        if ticker is None:

            priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

            log_cant_retrieve_ticker(order, msg_queue)
            return

        min_volume = compute_min_cap_from_ticker(order.pair_id, ticker)
        order_book = get_order_book(order.exchange_id, order.pair_id)

        if order_book is None:

            priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

            log_cant_retrieve_order_book(order, msg_queue)
            return

        orders = order_book.bid if order.trade_type == DEAL_TYPE.SELL else order_book.ask

        order.price = adjust_price_by_order_book(orders, order.volume)

        # Forcefully update balance for exchange - maybe other processes consume those coins
        update_balance_by_exchange(order.exchange_id)
        # Do we have enough coins at our balance
        balance = local_cache.get_balance(order.exchange_id)

        if balance.expired(BALANCE_EXPIRED_THRESHOLD):

            priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

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

        msg = "Replace existing order with new one - {tt}".format(tt=order)
        err_code, json_document = init_deal(order, msg)
        if err_code == STATUS.SUCCESS:

            order.execute_time = get_now_seconds_utc()
            order.order_book_time = long(order_book.timest)
            order.order_id = parse_order_id(order.exchange_id, json_document)

            msg_queue.add_order(ORDERS_MSG, order)

            priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

            log_placing_new_deal(order, msg_queue)
        else:
            log_cant_placing_new_deal(order, msg_queue)

            msg_queue.add_order(FAILED_ORDERS_MSG, order)
    else:
        print "NU VOT EPTA"


def update_executed_volume(open_orders_at_both_exchanges, every_deal):
    # FIXME NOTE: I do hate functions with side effects this is very vicious practice
    # Open question: how to do it properly?

    for deal in open_orders_at_both_exchanges:
        if deal == every_deal:
            if every_deal.exchange_id != EXCHANGE.POLONIEX:
                every_deal.volume = every_deal.volume - deal.executed_volume
                every_deal.executed_volume = deal.executed_volume
            else:
                every_deal.executed_volume = every_deal.volume - deal.volume
                every_deal.volume = deal.volume

            return True

    return False


def compute_time_key(timest, rounding_interval):
    return rounding_interval * long(timest / rounding_interval)


def add_orders_to_watch_list(orders_pair, priority_queue):

    if orders_pair is None:
        return

    msg = "Add order to watch list - {pair}".format(pair=str(orders_pair))
    log_to_file(msg, "expire_deal.log")

    # cache deals to be checked
    if orders_pair.deal_1 is not None:
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, orders_pair.deal_1)

    if orders_pair.deal_2 is not None:
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG,orders_pair.deal_2)
