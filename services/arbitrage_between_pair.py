import argparse

from decimal import Decimal

from data_access.message_queue import get_message_queue
from data_access.priority_queue import get_priority_queue
from data_access.classes.connection_pool import ConnectionPool
from data_access.memory_cache import get_cache

from core.arbitrage_core import search_for_arbitrage, adjust_currency_balance, \
    update_min_cap, is_order_books_expired
from core.expired_order import add_orders_to_watch_list

from data.balance_state import dummy_balance_init
from data.arbitrage_config import ArbitrageConfig
from data.market_cap import MarketCap

from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_books_for_arbitrage_pair
from dao.deal_utils import init_deals_with_logging_speedy

from utils.debug_utils import print_to_console, LOG_ALL_DEBUG, set_logging_level, set_log_folder

from enums.deal_type import DEAL_TYPE

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for
from utils.system_utils import die_hard

from logging_tools.arbitrage_between_pair_logging import log_dont_supported_currency, \
    log_balance_expired_errors, log_failed_to_retrieve_order_book

from constants import NO_MAX_CAP_LIMIT, BALANCE_EXPIRED_THRESHOLD, MIN_CAP_UPDATE_TIMEOUT, \
    YES_I_KNOW_WHAT_AM_I_DOING

from deploy.classes.common_settings import CommonSettings


def arbitrage_between_pair(args):
    cfg = ArbitrageConfig.from_args(args)

    app_settings = CommonSettings.from_cfg(args.cfg)

    set_logging_level(app_settings.logging_level_id)
    set_log_folder(app_settings.log_folder)
    load_keys(app_settings.key_path)

    priority_queue = get_priority_queue(host=app_settings.cache_host, port=app_settings.cache_port)
    msg_queue = get_message_queue(host=app_settings.cache_host, port=app_settings.cache_port)
    local_cache = get_cache(host=app_settings.cache_host, port=app_settings.cache_port)

    processor = ConnectionPool(pool_size=2)

    # to avoid time-consuming check in future - validate arguments here
    for exchange_id in [args.sell_exchange_id, args.buy_exchange_id]:
        pair_name = get_currency_pair_name_by_exchange_id(cfg.pair_id, exchange_id)
        if pair_name is None:
            log_dont_supported_currency(cfg, exchange_id, cfg.pair_id)
            exit()

    deal_cap = MarketCap(cfg.pair_id, get_now_seconds_utc())
    deal_cap.update_max_volume_cap(NO_MAX_CAP_LIMIT)
    update_min_cap(cfg, deal_cap, processor)

    balance_state = dummy_balance_init(timest=0, default_volume=Decimal("0"), default_available_volume=Decimal("0"))

    if not YES_I_KNOW_WHAT_AM_I_DOING:
        die_hard("LIVE TRADING!")

    while True:

        if get_now_seconds_utc() - deal_cap.last_updated > MIN_CAP_UPDATE_TIMEOUT:
            update_min_cap(cfg, deal_cap, processor)

        for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:
            cur_timest_sec = get_now_seconds_utc()

            method = search_for_arbitrage if mode_id == DEAL_TYPE.ARBITRAGE else adjust_currency_balance
            active_threshold = cfg.threshold if mode_id == DEAL_TYPE.ARBITRAGE else cfg.reverse_threshold

            balance_state = get_updated_balance_arbitrage(cfg, balance_state, local_cache)

            if balance_state.expired(cur_timest_sec, cfg.buy_exchange_id, cfg.sell_exchange_id,
                                     BALANCE_EXPIRED_THRESHOLD):
                log_balance_expired_errors(cfg, msg_queue, balance_state)
                die_hard("Balance expired")

            order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(cfg, cur_timest_sec, processor)

            if order_book_dst is None or order_book_src is None:
                log_failed_to_retrieve_order_book(cfg)
                sleep_for(3)
                continue

            if is_order_books_expired(order_book_src, order_book_dst, local_cache, msg_queue, cfg.log_file_name):
                sleep_for(3)
                continue

            local_cache.cache_order_book(order_book_src)
            local_cache.cache_order_book(order_book_dst)

            # init_deals_with_logging_speedy
            status_code, deal_pair = method(order_book_src, order_book_dst, active_threshold, cfg.balance_threshold,
                                            init_deals_with_logging_speedy,
                                            balance_state, deal_cap, type_of_deal=mode_id, worker_pool=processor,
                                            msg_queue=msg_queue)

            add_orders_to_watch_list(deal_pair, priority_queue)

            print_to_console("I am still alive! ", LOG_ALL_DEBUG)
            sleep_for(2)

        sleep_for(3)

        deal_cap.update_max_volume_cap(NO_MAX_CAP_LIMIT)


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

    parser.add_argument('--cfg', action="store", required=True)

    arguments = parser.parse_args()

    arbitrage_between_pair(arguments)
