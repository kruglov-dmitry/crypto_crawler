import argparse

from core.arbitrage_core import search_for_arbitrage, init_deals_with_logging_speedy, adjust_currency_balance
from core.backtest import common_cap_init, dummy_balance_init, dummy_order_state_init
from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_books_for_arbitrage_pair
from data.ArbitrageConfig import ArbitrageConfig
from data_access.ConnectionPool import ConnectionPool
from data_access.memory_cache import local_cache
from enums.deal_type import DEAL_TYPE
from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc
from utils.time_utils import sleep_for
from utils.exchange_utils import get_exchange_name_by_id


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
    cur_timest = get_now_seconds_utc()
    balance_state = dummy_balance_init(cur_timest, 0, 0)
    order_state = dummy_order_state_init()

    processor = ConnectionPool(pool_size=2)

    method = search_for_arbitrage if cfg.mode == DEAL_TYPE.ARBITRAGE else adjust_currency_balance

    while True:

        timest = get_now_seconds_utc()

        balance_state = get_updated_balance_arbitrage(cfg, balance_state, local_cache)

        order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(cfg, timest, processor)

        if order_book_dst is None or order_book_src is None:
            if order_book_dst is None:
                print "CAN'T retrieve order book for {nn}".format(nn=get_exchange_name_by_id(cfg.sell_exchange_id))
            sleep_for(1)
            continue

        method(order_book_src, order_book_dst, cfg.threshold, init_deals_with_logging_speedy,
               balance_state, deal_cap, type_of_deal=cfg.mode, worker_pool=processor)

        sleep_for(1)