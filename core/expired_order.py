from collections import defaultdict

from core.arbitrage_core import adjust_price_by_order_book, determine_maximum_volume_by_balance, \
    compute_min_cap_from_ticker, round_volume
from logging.expired_order_logging import log_cant_cancel_deal, log_placing_new_deal, log_cant_placing_new_deal, \
    log_cant_retrieve_order_book, log_dont_have_open_orders, log_open_orders_bad_result, \
    log_trace_all_open_orders, log_trace_log_time_key, log_trace_log_all_cached_orders_for_time_key, \
    log_trace_order_not_yet_expired, log_trace_processing_oder, log_trace_cancel_request_result, \
    log_trace_warched_orders_after_processing, log_open_orders_by_exchange_bad_result, log_open_orders_is_empty, \
    log_balance_expired, log_too_small_volume

from dao.order_utils import get_open_orders_for_arbitrage_pair, get_open_orders_by_exchange
from dao.ticker_utils import get_ticker
from dao.dao import cancel_by_exchange, parse_order_id
from dao.deal_utils import init_deal
from dao.order_book_utils import get_order_book

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc

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

        ticker = get_ticker(order.exchange_id, order.pair_id)
        min_volume = compute_min_cap_from_ticker(order.pair_id, ticker)
        order_book = get_order_book(order.exchange_id, order.pair_id)

        if order_book is not None:

            orders = order_book.bid if order.trade_type == DEAL_TYPE.SELL else order_book.ask

            order.price = adjust_price_by_order_book(orders, order.volume)

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
            log_cant_retrieve_order_book(order, msg_queue)


def process_expired_deals(list_of_orders, cfg, msg_queue, worker_pool):
    """
    Current approach to deal with tracked deals that expire.
    Details and discussion at https://gitlab.com/crypto_trade/crypto_crawler/issues/15

    :param list_of_orders:      tracked orders
    :param cfg:                 arbitrage settings, including order expire timeout
    :param msg_queue:           cache for Telegram notification
    :param worker_pool:         gevent based connection pool for speedy deal placement
    :return:
    """

    if len(list_of_orders) == 0:
        return

    err_code, open_orders_at_both_exchanges = get_open_orders_for_arbitrage_pair(cfg, worker_pool)
    if err_code == STATUS.FAILURE:
        log_open_orders_bad_result(cfg)
        return

    if len(open_orders_at_both_exchanges) == 0:
        log_dont_have_open_orders(cfg)
        list_of_orders.clear()
        return

    log_trace_all_open_orders(open_orders_at_both_exchanges)

    time_key = compute_time_key(get_now_seconds_utc(), cfg.deal_expire_timeout)

    log_trace_log_time_key(time_key)

    replaced_orders = defaultdict(list)
    problematic_expired_orders = defaultdict(list)

    for ts in list_of_orders:

        log_trace_log_all_cached_orders_for_time_key(list_of_orders, ts)

        if cfg.deal_expire_timeout > time_key - ts:
            log_trace_order_not_yet_expired(time_key, ts)
            continue

        orders_to_check = list_of_orders[ts]
        if len(orders_to_check) == 0:
            log_to_file("Size of deals_to_check is zero. Nothing to do. :(", "expire_deal.log")
            continue

        for every_order in orders_to_check:

            log_trace_processing_oder(every_order)

            if update_executed_volume(open_orders_at_both_exchanges, every_order):
                err_code, responce = cancel_by_exchange(every_order)

                log_trace_cancel_request_result(every_order, err_code, responce)

                if err_code == STATUS.FAILURE:
                    log_cant_cancel_deal(every_order, msg_queue, log_file_name=cfg.log_file_name)
                    problematic_expired_orders[ts].append(every_order)
                    continue

                order_book = get_order_book(every_order.exchange_id, every_order.pair_id)

                if order_book is not None:

                    orders = order_book.bid if every_order.trade_type == DEAL_TYPE.SELL else order_book.ask

                    new_price = adjust_price_by_order_book(orders, every_order.volume)
                    every_order.price = new_price
                    every_order.create_time = get_now_seconds_utc()

                    msg = "Replace existing deal with new one - {tt}".format(tt=every_order)
                    err_code, json_document = init_deal(every_order, msg)
                    if err_code == STATUS.SUCCESS:

                        every_order.execute_time = get_now_seconds_utc()
                        every_order.order_book_time = long(order_book.timest)
                        every_order.order_id = parse_order_id(every_order.exchange_id, json_document)

                        replaced_orders[ts].append(every_order)

                        msg_queue.add_order(ORDERS_MSG, every_order)

                        log_placing_new_deal(every_order, msg_queue, log_file_name=cfg.log_file_name)
                    else:
                        log_cant_placing_new_deal(every_order, msg_queue, log_file_name=cfg.log_file_name)
                        problematic_expired_orders[ts].append(every_order)
                else:
                    log_cant_retrieve_order_book(every_order, msg_queue, log_file_name=cfg.log_file_name)
                    problematic_expired_orders[ts].append(every_order)

    """
            So,
            As result of manipulation above what we have:
            failed orders grouped by time_key
            replaced orders grouped by time_key
            now we have to update our expired order queue
            
            first we will remove whatever we have for corresponding time key
            second fill it with new values from replacemnt and failed list to be tracked again
    """

    for every_key in replaced_orders:
        list_of_orders.pop(every_key)

    for every_key in problematic_expired_orders:
        list_of_orders[every_key] = problematic_expired_orders[every_key]

    for tt in replaced_orders:
        for every_order in replaced_orders[tt]:
            new_time_key = compute_time_key(every_order.execute_time, cfg.deal_expire_timeout)
            list_of_orders[new_time_key].append(every_order)

    log_trace_warched_orders_after_processing(list_of_orders)


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

    msg = "Add order to watch list - {pair}".format(pair=str(orders_pair))
    log_to_file(msg, "expire_deal.log")

    if orders_pair is None:
        return

    # cache deals to be checked
    if orders_pair.deal_1 is not None:
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, orders_pair.deal_1)

    if orders_pair.deal_2 is not None:
        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG,orders_pair.deal_2)
