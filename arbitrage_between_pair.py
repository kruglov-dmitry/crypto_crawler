from utils.key_utils import load_keys
from enums.deal_type import DEAL_TYPE
from core.backtest import common_cap_init, dummy_balance_init, dummy_order_state_init
from utils.time_utils import get_now_seconds_utc
from arbitrage_core import search_for_arbitrage, init_deals_with_logging
from data.ArbitrageConfig import ArbitrageConfig
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Constantly poll two exchange for order book for particular pair "
                                                 "and initiate sell\\buy deals for arbitrage opportunities")

    parser.add_argument('--threshold', action="store", type=float)
    parser.add_argument('--sell_exchange_id', action="store", type=int)
    parser.add_argument('--buy_exchange_id', action="store", type=int)
    parser.add_argument('--pair_id', action="store", type=int)
    parser.add_argument('--mode_id', action="store", type=int)

    results = parser.parse_args()

    cfg = ArbitrageConfig(results.threshold, results.sell_exchange_name, results.buy_exchange_name, results.pair_name, results.mode_name)

    load_keys("./secret_keys")

    deal_cap = common_cap_init()
    cur_timest = get_now_seconds_utc()
    balance_state = dummy_balance_init(cur_timest, 0, 0)
    order_state = dummy_order_state_init()

    while True:
        balance_state = get_updated_balance_for_both_exchange(src_exchange_id, dst_exchange_id, balance_state)

        order_book_src, order_book_dst = get_order_books_for_arbitrage_pair(src_exchange_id, dst_exchange_id, pair_id)

        search_for_arbitrage(cfg.sell_exchange_id,
                             cfg.buy_exchange_id,
                             cfg.threshold,
                             init_deals_with_logging,
                             balance_state,
                             deal_cap,
                             type_of_deal=DEAL_TYPE.ARBITRAGE)