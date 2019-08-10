from core.arbitrage_core import adjust_price_by_order_book, compute_min_cap_from_ticker, \
    place_order_by_market_rate
from logging_tools.expired_order_logging import log_cant_cancel_deal, \
    log_cant_retrieve_order_book, log_trace_all_open_orders, \
    log_trace_cancel_request_result, log_open_orders_by_exchange_bad_result, log_open_orders_is_empty, \
    log_balance_expired, log_cant_retrieve_ticker

from dao.order_utils import get_open_orders_by_exchange
from dao.ticker_utils import get_ticker
from dao.dao import cancel_by_exchange
from dao.order_book_utils import get_order_book, is_order_book_expired
from dao.balance_utils import update_balance_by_exchange

from utils.file_utils import log_to_file
from utils.time_utils import sleep_for
from utils.debug_utils import EXPIRED_ORDER_PROCESSING_FILE_NAME

from data_access.priority_queue import ORDERS_EXPIRE_MSG

from enums.status import STATUS
from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE

from constants import BALANCE_EXPIRED_THRESHOLD


def process_expired_order(expired_order, msg_queue, priority_queue, local_cache):
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

    :param expired_order:  order retrieved from redis cache
    :param msg_queue: saving to postgres and re-process failed orders
    :param priority_queue: watch queue for expired orders
    :param local_cache: to retrieve balance
    :return:
    """

    err_code, open_orders = get_open_orders_by_exchange(expired_order.exchange_id, expired_order.pair_id)

    if err_code == STATUS.FAILURE:
        log_open_orders_by_exchange_bad_result(expired_order)

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        return

    if not open_orders:
        log_open_orders_is_empty(expired_order)
        return

    log_trace_all_open_orders(open_orders)

    if not executed_volume_updated(open_orders, expired_order):
        log_to_file("Can't update volume for ", EXPIRED_ORDER_PROCESSING_FILE_NAME)

    err_code, responce = cancel_by_exchange(expired_order)

    log_trace_cancel_request_result(expired_order, err_code, responce)

    if err_code == STATUS.FAILURE:
        log_cant_cancel_deal(expired_order, msg_queue)

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        return

    # FIXME NOTE
    # so we want exchange update for us available balance
    # as we observe situation where its not happen immediately
    # we want to mitigate delay with this dirty workaround
    sleep_for(2)

    ticker = get_ticker(expired_order.exchange_id, expired_order.pair_id)
    if ticker is None:

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        log_cant_retrieve_ticker(expired_order, msg_queue)
        return

    min_volume = compute_min_cap_from_ticker(expired_order.pair_id, ticker)
    order_book = get_order_book(expired_order.exchange_id, expired_order.pair_id)

    if order_book is None:

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        log_cant_retrieve_order_book(expired_order, msg_queue)
        return

    if is_order_book_expired(EXPIRED_ORDER_PROCESSING_FILE_NAME, order_book, local_cache, msg_queue):

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        return

    orders = order_book.bid if expired_order.trade_type == DEAL_TYPE.SELL else order_book.ask

    expired_order.price = adjust_price_by_order_book(orders, expired_order.volume)

    # Forcefully update balance for exchange - maybe other processes consume those coins
    update_balance_by_exchange(expired_order.exchange_id)
    # Do we have enough coins at our balance
    balance = local_cache.get_balance(expired_order.exchange_id)

    if balance.expired(BALANCE_EXPIRED_THRESHOLD):

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        log_balance_expired(expired_order.exchange_id, BALANCE_EXPIRED_THRESHOLD, balance, msg_queue)

        assert False

    place_order_by_market_rate(expired_order, msg_queue, priority_queue, min_volume, balance,
                               order_book, EXPIRED_ORDER_PROCESSING_FILE_NAME)


def executed_volume_updated(open_orders_at_both_exchanges, expired_order):
    # FIXME NOTE: I do hate functions with side effects this is very vicious practice
    # Open question: how to do it properly?

    for deal in open_orders_at_both_exchanges:
        if deal == expired_order:
            if expired_order.exchange_id != EXCHANGE.POLONIEX:
                expired_order.volume = expired_order.volume - deal.executed_volume
                expired_order.executed_volume = deal.executed_volume
            else:
                expired_order.executed_volume = expired_order.volume - deal.volume
                expired_order.volume = deal.volume

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
    if orders_pair.deal_1:
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, orders_pair.deal_1)

    if orders_pair.deal_2:
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, orders_pair.deal_2)
