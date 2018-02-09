import argparse

from data_access.message_queue import get_message_queue, DEAL_INFO_MSG
from data_access.priority_queue import get_priority_queue, ORDERS_EXPIRE_MSG

from core.arbitrage_core import search_for_arbitrage, adjust_currency_balance
from core.expired_deal import add_orders_to_watch_list
from core.backtest import common_cap_init, dummy_balance_init

from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_books_for_arbitrage_pair
from dao.ticker_utils import get_ticker_for_arbitrage
from dao.deal_utils import init_deals_with_logging_speedy

from data.ArbitrageConfig import ArbitrageConfig

from data_access.classes.ConnectionPool import ConnectionPool
from data_access.memory_cache import local_cache

from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_DEBUG, set_logging_level

from enums.deal_type import DEAL_TYPE

from utils.currency_utils import split_currency_pairs, get_currency_pair_name_by_exchange_id
from utils.exchange_utils import get_exchange_name_by_id
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for

from constants import NO_MAX_CAP_LIMIT, BALANCE_EXPIRED_THRESHOLD, MIN_CAP_UPDATE_TIMEOUT


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


def log_dont_supported_currency(cfg, exchange_id):
    msg = "Not supported currency {idx}-{name} for {exch}".format(idx=cfg.pair_id, name=pair_name,
                                                                  exch=get_exchange_name_by_id(exchange_id))
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)


def compute_new_min_cap_from_tickers(tickers):
    min_price = 0.0

    for ticker in tickers:
        if ticker is not None:
            min_price = max(min_price, ticker.ask)

    if min_price != 0.0:
        return 0.004 / min_price

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
                """.format(op=str(deal_cap.get_min_cap(dst_currency_id)), rp=str(new_cap))
        log_to_file(msg, "cap_price_adjustment.log")

        deal_cap.update_min_cap(dst_currency_id, new_cap, cur_timest_sec)
    else:
        msg = """CAN'T update minimum_volume_cap for {pair_id} at following
        exchanges: {exch1} {exch2}""".format(pair_id=cfg.pair_id, exch1=get_exchange_name_by_id(cfg.buy_exchange_id),
                                             exch2=get_exchange_name_by_id(cfg.sell_exchange_id))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, cfg.log_file_name)
        log_to_file(msg, "cap_price_adjustment.log")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Constantly poll two exchange for order book for particular pair "
                                                 "and initiate sell\\buy deals for arbitrage opportunities")

    parser.add_argument('--threshold', action="store", type=float, required=True)
    parser.add_argument('--balance_threshold', action="store", type=float, required=True)
    parser.add_argument('--reverse_threshold', action="store", type=float, required=True)
    parser.add_argument('--sell_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--buy_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--pair_id', action="store", type=int, required=True)
    parser.add_argument('--deal_expire_timeout', action="store", type=int, required=True)

    parser.add_argument('--logging_level', action="store", type=int)

    results = parser.parse_args()

    cfg = ArbitrageConfig(results.sell_exchange_id, results.buy_exchange_id,
                          results.pair_id, results.threshold,
                          results.reverse_threshold, results.balance_threshold,
                          results.deal_expire_timeout,
                          results.logging_level)

    if cfg.logging_level_id is not None:
        set_logging_level(cfg.logging_level_id)

    load_keys("./secret_keys")

    # FIXME NOTE: read from config redis host \ port pass it to get_*_queue methods

    priority_queue = get_priority_queue()
    msg_queue = get_message_queue()

    processor = ConnectionPool(pool_size=2)

    # to avoid time-consuming check in future - validate arguments here
    for exchange_id in [results.sell_exchange_id, results.buy_exchange_id]:
        pair_name = get_currency_pair_name_by_exchange_id(cfg.pair_id, exchange_id)
        if pair_name is None:
            log_dont_supported_currency(cfg, exchange_id)
            exit()

    deal_cap = common_cap_init()
    update_min_cap(cfg, deal_cap, processor)
    deal_cap.update_max_cap(cfg.pair_id, NO_MAX_CAP_LIMIT)

    balance_state = dummy_balance_init(timest=0, default_volume=0, default_available_volume=0)

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
                log_balance_expired_errors(cfg, msg_queue)

                assert False

            order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(cfg, cur_timest_sec, processor)

            if order_book_dst is None or order_book_src is None:
                log_failed_to_retrieve_order_book(cfg)
                sleep_for(3)
                continue

            # init_deals_with_logging_speedy
            status_code, deal_pair = method(order_book_src, order_book_dst, active_threshold, cfg.balance_threshold,
                                            init_deals_with_logging_speedy,
                                            balance_state, deal_cap, type_of_deal=mode_id, worker_pool=processor,
                                            msg_queue=msg_queue)

            add_orders_to_watch_list(deal_pair, priority_queue)

            last_order_book[order_book_src.exchange_id] = order_book_src
            last_order_book[order_book_dst.exchange_id] = order_book_dst

            print_to_console("I am still allive! ", LOG_ALL_DEBUG)
            sleep_for(1)

        sleep_for(2)

        deal_cap.update_max_cap(cfg.pair_id, NO_MAX_CAP_LIMIT)