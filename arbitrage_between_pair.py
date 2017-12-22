import argparse

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
from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_DEBUG

BALANCE_EXPIRED_THRESHOLD = 60


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Constantly poll two exchange for order book for particular pair "
                                                 "and initiate sell\\buy deals for arbitrage opportunities")

    parser.add_argument('--threshold', action="store", type=float, required=True)
    parser.add_argument('--sell_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--buy_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--pair_id', action="store", type=int, required=True)
    parser.add_argument('--mode_id', action="store", type=int, required=True)

    results = parser.parse_args()

    cfg = ArbitrageConfig(results.threshold, results.sell_exchange_id, results.buy_exchange_id, results.pair_id, results.mode_id)

    load_keys("./secret_keys")

    deal_cap = common_cap_init()

    balance_state = dummy_balance_init(timest=0, default_volume=0, default_available_volume=0)

    processor = ConnectionPool(pool_size=2)

    method = search_for_arbitrage if cfg.mode == DEAL_TYPE.ARBITRAGE else adjust_currency_balance

    while True:

        timest = get_now_seconds_utc()

        balance_state = get_updated_balance_arbitrage(cfg, balance_state, local_cache)

        if balance_state.expired(timest, cfg.buy_exchange_id, cfg.sell_exchange_id, BALANCE_EXPIRED_THRESHOLD):
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

        order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(cfg, timest, processor)

        if order_book_dst is None or order_book_src is None:
            if order_book_dst is None:
                print "CAN'T retrieve order book for {nn}".format(nn=get_exchange_name_by_id(cfg.sell_exchange_id))
            sleep_for(1)
            continue

        # init_deals_with_logging_speedy
        method(order_book_src, order_book_dst, cfg.threshold,
               init_deals_with_logging_speedy,
               balance_state, deal_cap, type_of_deal=cfg.mode, worker_pool=processor)

        print_to_console("I am still allive! ", LOG_ALL_DEBUG)
        sleep_for(1)