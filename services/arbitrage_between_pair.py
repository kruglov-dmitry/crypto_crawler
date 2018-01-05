import argparse
from collections import defaultdict

from data_access.message_queue import get_message_queue, DEAL_INFO_MSG

from core.arbitrage_core import search_for_arbitrage, adjust_currency_balance, adjust_price_by_order_book
from core.backtest import common_cap_init, dummy_balance_init

from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_books_for_arbitrage_pair
from dao.order_utils import get_open_orders_for_arbitrage_pair
from dao.ticker_utils import get_ticker_for_arbitrage
from dao.dao import cancel_by_exchange, parse_deal_id_by_exchange_id
from dao.deal_utils import init_deal, init_deals_with_logging_speedy

from data.ArbitrageConfig import ArbitrageConfig

from data_access.classes.ConnectionPool import ConnectionPool
from data_access.memory_cache import local_cache

from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_DEBUG, set_logging_level

from enums.deal_type import DEAL_TYPE
from enums.status import STATUS

from utils.currency_utils import split_currency_pairs
from utils.exchange_utils import get_exchange_name_by_id
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for

BALANCE_EXPIRED_THRESHOLD = 60
MIN_CAP_UPDATE_TIMEOUT = 900


def log_balance_expired_errors(cfg, msg_queue):
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


def log_cant_cancel_deal(every_deal, cfg, msg_queue):
    msg = "CAN'T cancel deal - {deal}".format(deal=every_deal)

    msg_queue.add_message(DEAL_INFO_MSG, msg)

    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)


def log_placing_new_deal(every_deal, cfg, msg_queue):
    msg = """ We try to send following deal to exchange as replacement for expired order.
    Deal details: {deal}""".format(deal=str(every_deal))

    log_to_file(msg, cfg.log_file_name)

    msg_queue.add_message(DEAL_INFO_MSG, msg)

    print_to_console(msg, LOG_ALL_ERRORS)


def log_cant_placing_new_deal(every_deal, cfg, msg_queue):
    msg = """   We <b> !!! FAILED !!! </b>
    to send following deal to exchange as replacement for expired order.
    Deal details:
    {deal}
    """.format(deal=str(every_deal))

    log_to_file(msg, cfg.log_file_name)

    msg_queue.add_message(DEAL_INFO_MSG, msg)

    print_to_console(msg, LOG_ALL_ERRORS)


def log_cant_find_order_book(every_deal, cfg, msg_queue):
    msg = """ Can't find order book for deal with expired orders!
        Order details: {deal}""".format(deal=str(every_deal))

    log_to_file(msg, cfg.log_file_name)

    msg_queue.add_message(DEAL_INFO_MSG, msg)

    print_to_console(msg, LOG_ALL_ERRORS)


def deal_is_not_closed(open_orders_at_both_exchanges, every_deal):
    for deal in open_orders_at_both_exchanges:
        if deal == every_deal:
            return True

    return False


def compute_new_min_cap_from_tickers(tickers):
    min_price = 0.0

    for ticker in tickers:
        min_price = max(min_price, ticker.ask)

    if min_price != 0.0:
        return 0.002 / min_price

    return 0.0


def update_min_cap(cfg, deal_cap, processor):
    cur_timest_sec = get_now_seconds_utc()
    tickers = get_ticker_for_arbitrage(cfg.pair_id, cur_timest_sec,
                                       [cfg.buy_exchange_id, cfg.sell_exchange_id], processor)
    new_cap = compute_new_min_cap_from_tickers(tickers)

    if new_cap > 0:
        base_currency_id, dst_currency_id = split_currency_pairs(cfg.pair_id)
        msg = """old cap {op}:
                new_cap: {rp}
                """.format(op=str(deal_cap.min_volume_cap[dst_currency_id]), rp=str(new_cap))
        log_to_file(msg, "price_adjustment.log")
        deal_cap.update_min_cap(dst_currency_id, new_cap, cur_timest_sec)
    else:
        msg = """CAN'T update minimum_volume_cap for {pair_id} at following
        exchanges: {exch1} {exch2}""".format(pair_id=cfg.pair_id, exch1=get_exchange_name_by_id(cfg.buy_exchange_id),
                                             exch2=get_exchange_name_by_id(cfg.sell_exchange_id))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, cfg.log_file_name)
        log_to_file(msg, "price_adjustment.log")

def add_deals_to_watch_list(list_of_deals, deal_pair):
    if deal_pair is None:
        return
    # cache deals to be checked
    if deal_pair.deal_1 is not None:
        time_key = long(deal_pair.deal_1.execute_time / cfg.deal_expire_timeout)
        list_of_deals[time_key].append(deal_pair.deal_1)
    if deal_pair.deal_2 is not None:
        time_key = long(deal_pair.deal_2.execute_time / cfg.deal_expire_timeout)
        list_of_deals[time_key].append(deal_pair.deal_2)


def process_expired_deals(list_of_deals, cfg, msg_queue):
    """
    Current approach to deal with tracked deals that expire.
    Details and discussion at https://gitlab.com/crypto_trade/crypto_crawler/issues/15

    :param list_of_deals: tracked deals
    :param cfg: arbitrage settings, includeing deal expire timeout
    :param msg_queue: cache for Telegram notification
    :return:
    """
    time_key = long(get_now_seconds_utc() / cfg.deal_expire_timeout)

    for ts in list_of_deals:
        if cfg.deal_expire_timeout > time_key - ts:
            continue

        deals_to_check = list_of_deals[ts]
        if len(deals_to_check) == 0:
            continue

        updated_list = []

        open_orders_at_both_exchanges = get_open_orders_for_arbitrage_pair(cfg, processor)
        for every_deal in deals_to_check:
            if deal_is_not_closed(open_orders_at_both_exchanges, every_deal):
                err_code, responce = cancel_by_exchange(every_deal)
                if err_code == STATUS.FAILURE:
                    log_cant_cancel_deal(every_deal, cfg, msg_queue)
                    updated_list.append(every_deal)

                if every_deal.exchange_id in last_order_book:
                    orders = last_order_book[every_deal.exchange_id].bid if every_deal.trade_type == DEAL_TYPE.SELL else last_order_book[every_deal.exchange_id].ask
                    new_price = adjust_price_by_order_book(orders, every_deal.volume)
                    every_deal.price = new_price
                    every_deal.create_time = get_now_seconds_utc()
                    msg = "Replace existing deal with new one - {tt}".format(tt=every_deal)
                    err_code, json_document = init_deal(every_deal, msg)
                    if err_code == STATUS.SUCCESS:

                        new_time_key = long(get_now_seconds_utc() / cfg.deal_expire_timeout)
                        list_of_deals[new_time_key].append(every_deal)

                        every_deal.execute_time = get_now_seconds_utc()
                        every_deal.order_book_time = long(last_order_book[every_deal.exchange_id].timest)
                        every_deal.deal_id = parse_deal_id_by_exchange_id(every_deal.exchange_id, json_document)

                        log_placing_new_deal(every_deal, cfg, msg_queue)
                    else:
                        log_cant_placing_new_deal(every_deal, cfg, msg_queue)
                else:
                    log_cant_find_order_book(every_deal, cfg, msg_queue)
                    updated_list.append(every_deal)

        # Hopefully it is empty
        list_of_deals[ts] = updated_list


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Constantly poll two exchange for order book for particular pair "
                                                 "and initiate sell\\buy deals for arbitrage opportunities")

    parser.add_argument('--threshold', action="store", type=float, required=True)
    parser.add_argument('--reverse_threshold', action="store", type=float, required=True)
    parser.add_argument('--sell_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--buy_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--pair_id', action="store", type=int, required=True)
    parser.add_argument('--deal_expire_timeout', action="store", type=int, required=True)

    parser.add_argument('--logging_level', action="store", type=int)

    results = parser.parse_args()

    cfg = ArbitrageConfig(results.sell_exchange_id, results.buy_exchange_id,
                          results.pair_id, results.threshold,
                          results.reverse_threshold, results.deal_expire_timeout,
                          results.logging_level)

    if cfg.logging_level_id is not None:
        set_logging_level(cfg.logging_level_id)

    # FIXME to log
    print cfg

    msg_queue1 = get_message_queue()
    processor = ConnectionPool(pool_size=2)

    load_keys("./secret_keys")

    deal_cap = common_cap_init()
    update_min_cap(cfg, deal_cap, processor)

    balance_state = dummy_balance_init(timest=0, default_volume=0, default_available_volume=0)

    # key is timest rounded to minutes
    list_of_deals = defaultdict(list)

    last_order_book = {}

    while True:

        if get_now_seconds_utc() - deal_cap.last_updated > MIN_CAP_UPDATE_TIMEOUT:
            update_min_cap(cfg, deal_cap, processor)

        for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:
            cur_timest_sec = get_now_seconds_utc()

            method = search_for_arbitrage if mode_id == DEAL_TYPE.ARBITRAGE else adjust_currency_balance
            active_threshold = cfg.threshold if mode_id == DEAL_TYPE.ARBITRAGE else cfg.reverse_threshold

            balance_state = get_updated_balance_arbitrage(cfg, balance_state, local_cache)

            if balance_state.expired(cur_timest_sec, cfg.buy_exchange_id, cfg.sell_exchange_id, BALANCE_EXPIRED_THRESHOLD):
                log_balance_expired_errors(cfg, msg_queue1)
                raise

            order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(cfg, cur_timest_sec, processor)

            if order_book_dst is None or order_book_src is None:
                log_failed_to_retrieve_order_book(cfg)
                sleep_for(1)
                continue

            # init_deals_with_logging_speedy
            status_code, deal_pair = method(order_book_src, order_book_dst, active_threshold,
                                            init_deals_with_logging_speedy,
                                            balance_state, deal_cap, type_of_deal=mode_id, worker_pool=processor,
                                            msg_queue=msg_queue1)

            add_deals_to_watch_list(list_of_deals, deal_pair)

            last_order_book[order_book_src.exchange_id] = order_book_src
            last_order_book[order_book_dst.exchange_id] = order_book_dst

            print_to_console("I am still allive! ", LOG_ALL_DEBUG)
            sleep_for(1)

        process_expired_deals(list_of_deals, cfg, msg_queue1)
