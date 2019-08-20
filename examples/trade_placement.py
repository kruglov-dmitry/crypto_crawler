"""
        Routine that demonstrate usage of some sub-set of functionality
"""

from binance.buy_utils import add_buy_order_binance

from dao.deal_utils import init_deals_with_logging_speedy
from data.trade import Trade
from data.trade_pair import TradePair
from data_access.classes.connection_pool import ConnectionPool

from enums.currency_pair import CURRENCY_PAIR
from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE

from poloniex.buy_utils import add_buy_order_poloniex

from bittrex.buy_utils import add_buy_order_bittrex
from bittrex.sell_utils import add_sell_order_bittrex

from utils.key_utils import load_keys, get_key_by_exchange
from utils.time_utils import get_now_seconds_utc
from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.system_utils import die_hard

from data_access.message_queue import get_message_queue

from constants import YES_I_KNOW_WHAT_AM_I_DOING, API_KEY_PATH


def check_deal_placements():
    if not YES_I_KNOW_WHAT_AM_I_DOING:
        die_hard("check_deal_placements may issue a real trade!")

    create_time = get_now_seconds_utc()
    fake_order_book_time1 = -10
    fake_order_book_time2 = -20
    deal_volume = 5
    pair_id = CURRENCY_PAIR.BTC_TO_ARDR

    sell_exchange_id = EXCHANGE.POLONIEX
    buy_exchange_id = EXCHANGE.BITTREX

    difference = "difference is HUGE"
    file_name = "test.log"

    msg_queue = get_message_queue()

    processor = ConnectionPool(pool_size=2)

    trade_at_first_exchange = Trade(DEAL_TYPE.SELL, sell_exchange_id, pair_id,
                                    0.00000001, deal_volume, fake_order_book_time1,
                                    create_time)

    trade_at_second_exchange = Trade(DEAL_TYPE.BUY, buy_exchange_id, pair_id,
                                     0.00004, deal_volume, fake_order_book_time2,
                                     create_time)

    trade_pairs = TradePair(trade_at_first_exchange, trade_at_second_exchange, fake_order_book_time1, fake_order_book_time2, DEAL_TYPE.DEBUG)

    init_deals_with_logging_speedy(trade_pairs, difference, file_name, processor, msg_queue)

#
#       For testing new currency pair
#


def test_binance_xlm():
    if not YES_I_KNOW_WHAT_AM_I_DOING:
        die_hard("test_binance_xlm may issue a real trade!")

    load_keys(API_KEY_PATH)
    key = get_key_by_exchange(EXCHANGE.BINANCE)
    pair_id = CURRENCY_PAIR.BTC_TO_XLM
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.BINANCE)
    err, json_repr = add_buy_order_binance(key, pair_name, price=0.00003000, amount=100)
    print json_repr


def test_poloniex_doge():
    if not YES_I_KNOW_WHAT_AM_I_DOING:
        die_hard("test_poloniex_doge may issue a real trade!")

    load_keys(API_KEY_PATH)
    key = get_key_by_exchange(EXCHANGE.POLONIEX)
    pair_id = CURRENCY_PAIR.BTC_TO_DGB
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.POLONIEX)
    err, json_repr = add_buy_order_poloniex(key, pair_name, price=0.00000300, amount=100)
    print json_repr


def test_bittrex_strat():
    if not YES_I_KNOW_WHAT_AM_I_DOING:
        die_hard("test_bittrex_strat may issue a real trade!")

    key = get_key_by_exchange(EXCHANGE.BITTREX)
    pair_id = CURRENCY_PAIR.BTC_TO_STRAT
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.BITTREX)
    err, json_repr = add_buy_order_bittrex(key, pair_name, price=0.0007, amount=10)
    print json_repr
    err, json_repr = add_sell_order_bittrex(key, pair_name, price=0.0015, amount=10)
    print json_repr
