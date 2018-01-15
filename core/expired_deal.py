from collections import defaultdict

from core.arbitrage_core import adjust_price_by_order_book
from core.expired_deal_logging import log_cant_cancel_deal, log_placing_new_deal, log_cant_placing_new_deal, \
    log_cant_find_order_book, log_dont_have_open_orders, log_open_orders_bad_result

from dao.order_utils import get_open_orders_for_arbitrage_pair
from dao.dao import cancel_by_exchange, parse_deal_id_from_json_by_exchange_id
from dao.deal_utils import init_deal

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc

from enums.status import STATUS
from enums.deal_type import DEAL_TYPE


def process_expired_deals(list_of_deals, last_order_book, cfg, msg_queue, processor):
    """
    Current approach to deal with tracked deals that expire.
    Details and discussion at https://gitlab.com/crypto_trade/crypto_crawler/issues/15

    :param list_of_deals: tracked deals
    :param cfg: arbitrage settings, includeing deal expire timeout
    :param msg_queue: cache for Telegram notification
    :return:
    """

    if len(list_of_deals) == 0:
        return

    open_orders_at_both_exchanges = get_open_orders_for_arbitrage_pair(cfg, processor)
    if len(open_orders_at_both_exchanges) == 0:
        log_dont_have_open_orders(cfg)
        list_of_deals.clear()
        return

    if None in open_orders_at_both_exchanges:
        log_open_orders_bad_result(cfg)
        return

    # REMOVE ME I AM DEBUG
    log_to_file("Open orders below:", "expire_deal.log")
    for v in open_orders_at_both_exchanges:
        log_to_file(v, "expire_deal.log")
    # REMOVE ME I AM DEBUG

    time_key = compute_time_key(get_now_seconds_utc(), cfg.deal_expire_timeout)

    # REMOVE ME I AM DEBUG
    msg = "process_expired_deals - for time key - {tk}".format(tk=str(time_key))
    log_to_file(msg, "expire_deal.log")
    # REMOVE ME I AM DEBUG

    replacement_deals = defaultdict(list)
    problematic_expired_orders = defaultdict(list)

    for ts in list_of_deals:

        # REMOVE ME I AM DEBUG
        log_to_file("For key {ts} in cached orders - {num} orders".format(ts=ts, num=len(list_of_deals[ts])),
                    "expire_deal.log")
        for bbb in list_of_deals[ts]:
            log_to_file(str(bbb), "expire_deal.log")
        # REMOVE ME I AM DEBUG

        if cfg.deal_expire_timeout > time_key - ts:
            # REMOVE ME I AM DEBUG
            msg = "Too early for processing this key: {kkk} but ts={ts}".format(kkk=time_key, ts=ts)
            log_to_file(msg, "expire_deal.log")
            # REMOVE ME I AM DEBUG
            continue

        deals_to_check = list_of_deals[ts]
        if len(deals_to_check) == 0:
            log_to_file("THIS CRAP IS ZERO?", "expire_deal.log")
            continue

        for every_deal in deals_to_check:

            # REMOVE ME I AM DEBUG
            msg = "Check deal from watch list - {pair}".format(pair=str(every_deal))
            log_to_file(msg, "expire_deal.log")

            if deal_is_not_closed(open_orders_at_both_exchanges, every_deal):
                err_code, responce = cancel_by_exchange(every_deal)

                # REMOVE ME I AM DEBUG
                msg = "We canceling deal - {dd} and raw result is {er_code} {js}".format(dd=str(every_deal),
                                                                                         er_code=str(err_code),
                                                                                         js=responce)
                print msg
                log_to_file(msg, "expire_deal.log")

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

                        replacement_deals[ts].append(every_deal)

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
            failed deal with time_key
            replaced_deal with time_key
            now we have to update our expired deal buffer
    """

    for every_key in replacement_deals:
        list_of_deals.pop(every_key)

    for every_key in problematic_expired_orders:
        list_of_deals.pop(every_key)

    for tt in problematic_expired_orders:
        list_of_deals[tt] = problematic_expired_orders[tt]

    for tt in replacement_deals:
        for every_order in replacement_deals[tt]:
            new_time_key = compute_time_key(every_order.execute_time, cfg.deal_expire_timeout)
            list_of_deals[new_time_key].append(every_order)

    # REMOVE ME I AM DEBUG
    for tkey in list_of_deals:
        msg = "For ts = {ts} cached deals are:".format(ts=str(tkey))
        log_to_file(msg, "expire_deal.log")
        for b in list_of_deals[tkey]:
            log_to_file(str(b), "expire_deal.log")
    # REMOVE ME I AM DEBUG


def deal_is_not_closed(open_orders_at_both_exchanges, every_deal):
    # FIXME NOTE: I do hate functions with side effects this is very vicious practice
    for deal in open_orders_at_both_exchanges:
        if deal == every_deal:
            every_deal.volume = every_deal.volume - deal.executed_volume
            return True

    return False


def compute_time_key(timest, rounding_interval):
    return rounding_interval * long(timest / rounding_interval)


def add_deals_to_watch_list(list_of_deals, deal_pair, cfg):
    if deal_pair is not None:
        msg = "Add order to watch list - {pair}".format(pair=str(deal_pair))
        log_to_file(msg, "expire_deal.log")
    if deal_pair is None:
        return
    # cache deals to be checked
    if deal_pair.deal_1 is not None:
        ts = deal_pair.deal_1.execute_time
        if ts is None:
            ts = deal_pair.deal_1.create_time
        time_key = compute_time_key(ts, cfg.deal_expire_timeout)
        list_of_deals[time_key].append(deal_pair.deal_1)
    if deal_pair.deal_2 is not None:
        ts = deal_pair.deal_2.execute_time
        if ts is None:
            ts = deal_pair.deal_2.create_time
        time_key = compute_time_key(ts, cfg.deal_expire_timeout)
        list_of_deals[time_key].append(deal_pair.deal_2)
