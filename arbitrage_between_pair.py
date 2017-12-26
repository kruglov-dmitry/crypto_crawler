import argparse
from collections import defaultdict

from core.arbitrage_core import search_for_arbitrage, init_deals_with_logging_speedy, adjust_currency_balance, \
    init_deals_with_logging_speedy_fake
from core.backtest import common_cap_init, dummy_balance_init, dummy_order_state_init

from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_books_for_arbitrage_pair
from data.ArbitrageConfig import ArbitrageConfig

from data_access.ConnectionPool import ConnectionPool
from data_access.memory_cache import local_cache
from data_access.telegram_notifications import send_single_message

from enums.deal_type import DEAL_TYPE
from enums.notifications import NOTIFICATION

from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for
from utils.file_utils import log_to_file
from utils.exchange_utils import get_exchange_name_by_id

from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_DEBUG, set_logging_level

BALANCE_EXPIRED_THRESHOLD = 60


def get_list_of_expired_deals(deals):
    return []


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

    cfg = ArbitrageConfig(results.threshold, results.reverse_threshold, results.sell_exchange_id,
                          results.buy_exchange_id, results.pair_id, results.deal_expire_timeout, results.logging_level)

    if cfg.logging_level_id is not None:
        set_logging_level(cfg.logging_level_id)

    load_keys("./secret_keys")

    deal_cap = common_cap_init()

    balance_state = dummy_balance_init(timest=0, default_volume=0, default_available_volume=0)

    processor = ConnectionPool(pool_size=2)

    # key is timest rounded to minutes
    list_of_deals = defaultdict(list)

    while True:

        for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:
            cur_timest_sec = get_now_seconds_utc()

            method = search_for_arbitrage if mode_id == DEAL_TYPE.ARBITRAGE else adjust_currency_balance
            active_threshold = cfg.threshold if mode_id == DEAL_TYPE.ARBITRAGE else cfg.reverse_threshold

            balance_state = get_updated_balance_arbitrage(cfg, balance_state, local_cache)

            if balance_state.expired(cur_timest_sec, cfg.buy_exchange_id, cfg.sell_exchange_id, BALANCE_EXPIRED_THRESHOLD):
                msg = """
                            <b> !!! CRITICAL !!! </b>
                Balance is OUTDATED for {exch1} or {exch2} for more than {tt} seconds
                Arbitrage process will be stopped just in case.
                Check log file: {lf}
                """.format(
                    exch1=get_exchange_name_by_id(cfg.buy_exchange_id),
                    exch2=get_exchange_name_by_id(cfg.sell_exchange_id),
                    tt=BALANCE_EXPIRED_THRESHOLD,
                    lf=cfg.log_file_name
                )
                print_to_console(msg, LOG_ALL_ERRORS)
                send_single_message(msg, NOTIFICATION.DEAL)
                log_to_file(msg, cfg.log_file_name)
                log_to_file(balance_state, cfg.log_file_name)
                raise

            order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(cfg, cur_timest_sec, processor)

            if order_book_dst is None or order_book_src is None:
                if order_book_dst is None:
                    msg = "CAN'T retrieve order book for {nn}".format(nn=get_exchange_name_by_id(cfg.sell_exchange_id))
                    print_to_console(msg, LOG_ALL_ERRORS)
                    log_to_file(msg, cfg.log_file_name)
                    print

                sleep_for(1)
                continue

            # init_deals_with_logging_speedy
            status_code, deal_pair = method(order_book_src, order_book_dst, active_threshold,
                                            init_deals_with_logging_speedy,
                                            balance_state, deal_cap, type_of_deal=mode_id, worker_pool=processor)

            print_to_console("I am still allive! ", LOG_ALL_DEBUG)
            sleep_for(1)

            deals_to_check = get_list_of_expired_deals(cur_timest_sec)
            if len(deals_to_check) > 0:
                deals_state = get_deals_state_by_exchange_speedup(cfg, processor)
                for every_deal in deals_to_check:
                    if deal_is_not_closed(deals_state, every_deal):
                        close_deal_by_exchange(every_deal)
