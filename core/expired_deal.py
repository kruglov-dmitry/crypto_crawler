from collections import defaultdict

from core.arbitrage_core import adjust_price_by_order_book
from core.expired_deal_logging import log_cant_cancel_deal, log_placing_new_deal, log_cant_placing_new_deal, \
    log_cant_find_order_book, log_dont_have_open_orders, log_open_orders_bad_result, \
    log_trace_all_open_orders, log_trace_log_time_key, log_trace_log_all_cached_orders_for_time_key, \
    log_trace_order_not_yet_expired, log_trace_processing_oder, log_trace_cancel_request_result, \
    log_trace_warched_orders_after_processing

from dao.order_utils import get_open_orders_for_arbitrage_pair
from dao.dao import cancel_by_exchange, parse_deal_id_from_json_by_exchange_id
from dao.deal_utils import init_deal

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc

from data_access.message_queue import ORDERS_MSG

from enums.status import STATUS
from enums.deal_type import DEAL_TYPE


def process_expired_deals(list_of_orders, last_order_book, cfg, msg_queue, worker_pool):
    """
    Current approach to deal with tracked deals that expire.
    Details and discussion at https://gitlab.com/crypto_trade/crypto_crawler/issues/15

    :param list_of_orders:      tracked orders
    :param last_order_book:     recent version of order_book for exchange
    :param cfg:                 arbitrage settings, including order expire timeout
    :param msg_queue:           cache for Telegram notification
    :param worker_pool:         gevent based connection pool for speedy deal placement
    :return:
    """

    if len(list_of_orders) == 0:
        return

    open_orders_at_both_exchanges = get_open_orders_for_arbitrage_pair(cfg, worker_pool)
    if len(open_orders_at_both_exchanges) == 0:
        log_dont_have_open_orders(cfg)
        list_of_orders.clear()
        return

    if None in open_orders_at_both_exchanges:
        log_open_orders_bad_result(cfg)
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

        deals_to_check = list_of_orders[ts]
        if len(deals_to_check) == 0:
            log_to_file("Size of deals_to_check is zero. Nothing to do. :(", "expire_deal.log")
            continue

        for every_deal in deals_to_check:

            log_trace_processing_oder(every_deal)

            if deal_is_not_closed(open_orders_at_both_exchanges, every_deal):
                err_code, responce = cancel_by_exchange(every_deal)

                log_trace_cancel_request_result(every_deal, err_code, responce)

                if err_code == STATUS.FAILURE:
                    log_cant_cancel_deal(every_deal, cfg, msg_queue)
                    problematic_expired_orders[ts].append(every_deal)
                    continue

                if every_deal.exchange_id in last_order_book:

                    orders = last_order_book[every_deal.exchange_id].bid if every_deal.trade_type == DEAL_TYPE.SELL else last_order_book[every_deal.exchange_id].ask

                    new_price = adjust_price_by_order_book(orders, every_deal.volume)
                    every_deal.price = new_price
                    every_deal.create_time = get_now_seconds_utc()

                    msg = "Replace existing deal with new one - {tt}".format(tt=every_deal)
                    err_code, json_document = init_deal(every_deal, msg)
                    if err_code == STATUS.SUCCESS:

                        every_deal.execute_time = get_now_seconds_utc()
                        every_deal.order_book_time = long(last_order_book[every_deal.exchange_id].timest)
                        every_deal.deal_id = parse_deal_id_from_json_by_exchange_id(every_deal.exchange_id, json_document)

                        replaced_orders[ts].append(every_deal)

                        msg_queue.add_order(ORDERS_MSG, every_deal)

                        log_placing_new_deal(every_deal, cfg, msg_queue)
                    else:
                        log_cant_placing_new_deal(every_deal, cfg, msg_queue)
                        problematic_expired_orders[ts].append(every_deal)
                else:
                    log_cant_find_order_book(every_deal, cfg, msg_queue)
                    problematic_expired_orders[ts].append(every_deal)

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
        list_of_orders.pop(every_key)

    for tt in problematic_expired_orders:
        list_of_orders[tt] = problematic_expired_orders[tt]

    for tt in replaced_orders:
        for every_order in replaced_orders[tt]:
            new_time_key = compute_time_key(every_order.execute_time, cfg.deal_expire_timeout)
            list_of_orders[new_time_key].append(every_order)

    log_trace_warched_orders_after_processing(list_of_orders)


def deal_is_not_closed(open_orders_at_both_exchanges, every_deal):
    # FIXME NOTE: I do hate functions with side effects this is very vicious practice
    # Open question: how to do it properly?
    
    for deal in open_orders_at_both_exchanges:
        if deal == every_deal:
            every_deal.volume = every_deal.volume - deal.executed_volume
            return True

    return False


def compute_time_key(timest, rounding_interval):
    return rounding_interval * long(timest / rounding_interval)


def add_orders_to_watch_list(list_of_orders, orders_pair, cfg):

    msg = "Add order to watch list - {pair}".format(pair=str(orders_pair))
    log_to_file(msg, "expire_deal.log")

    if orders_pair is None:
        return

    # cache deals to be checked
    if orders_pair.deal_1 is not None:
        ts = orders_pair.deal_1.execute_time
        if ts is None:
            ts = orders_pair.deal_1.create_time
        time_key = compute_time_key(ts, cfg.deal_expire_timeout)
        list_of_orders[time_key].append(orders_pair.deal_1)

    if orders_pair.deal_2 is not None:
        ts = orders_pair.deal_2.execute_time
        if ts is None:
            ts = orders_pair.deal_2.create_time
        time_key = compute_time_key(ts, cfg.deal_expire_timeout)
        list_of_orders[time_key].append(orders_pair.deal_2)
