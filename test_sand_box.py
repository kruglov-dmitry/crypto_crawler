from enums.exchange import EXCHANGE
from enums.currency import CURRENCY
from utils.key_utils import load_keys, get_key_by_exchange
from utils.time_utils import sleep_for, get_now_seconds_utc, get_now_seconds_local
from bittrex.market_utils import get_balance_bittrex
from poloniex.market_utils import get_balance_poloniex, get_orders_history_poloniex, get_open_orders_poloniex
from arbitrage_core import dummy_order_state_init
from dao.dao import get_updated_order_state
from bittrex.market_utils import add_buy_order_bittrex, add_sell_order_bittrex, \
    cancel_order_bittrex
from kraken.market_utils import get_orders_kraken, get_balance_kraken, add_buy_order_kraken, \
    add_sell_order_kraken, cancel_order_kraken

from binance.ticker_utils import get_tickers_binance
from binance.ohlc_utils import get_ohlc_binance
from binance.constants import BINANCE_CURRENCY_PAIRS
from binance.order_book_utils import get_order_book_binance
from binance.market_utils import add_buy_order_binance, add_sell_order_binance, \
    cancel_order_binance, get_balance_binance

from data_access.memory_cache import generate_nonce
from profilehooks import timecall
from dao.ohlc_utils import get_ohlc_speedup, get_ohlc
from dao.ticker_utils import get_ticker_speedup
from data_access.ConnectionPool import ConnectionPool

from dao.ohlc_utils import get_ohlc_speedup
from dao.order_book_utils import get_order_book_speedup
from dao.history_utils import get_history_speedup

POLL_PERIOD_SECONDS = 900

def test_binance_ticker_retrieval():
    timest = get_now_seconds_local()
    wtf = get_tickers_binance(BINANCE_CURRENCY_PAIRS, timest)
    for b in wtf:
        print wtf[b]


def test_binance_ohlc_retrieval():
    date_end = get_now_seconds_utc()
    date_start = date_end - 900
    all_ohlc = []
    for currency in BINANCE_CURRENCY_PAIRS:
        period = "15m"
        all_ohlc += get_ohlc_binance(currency, date_start, date_end, period)

    for b in all_ohlc:
        print b


def test_binance_order_book_retrieval():
    res = []
    timest = get_now_seconds_utc()
    for currency in BINANCE_CURRENCY_PAIRS:
        order_book = get_order_book_binance(currency, timest)
        if order_book is not None:
            res.append(order_book)

    for r in res:
        print r


def test_bittrex_market_api(bit_key):
    get_balance_bittrex(bit_key)
    cancel_order_bittrex(bit_key, '0e2ffb00-3509-4150-a7d2-f2b7e8c1a9e4')
    add_buy_order_bittrex(bit_key, "BTC-OMG", 0.00249870, 1)
    add_sell_order_bittrex(bit_key, "BTC-OMG", 0.0025, 1)


def test_kraken_placing_deals(krak_key):
    order_state = dummy_order_state_init()
    order_state = get_updated_order_state(order_state)

    for x in order_state[EXCHANGE.KRAKEN].open_orders:
        if x.pair_id == CURRENCY.BCC and x.volume == 0.1 and x.price == 0.5:
            cancel_order_kraken(krak_key, x.deal_id)

    order_state = get_updated_order_state(order_state)
    cnt = 0
    for x in order_state[EXCHANGE.KRAKEN].open_orders:
        if x.pair_id == CURRENCY.BCC and x.volume == 0.1 and x.price == 0.5:
            cnt += 1
            print x

    print cnt

    print order_state[EXCHANGE.KRAKEN]
    ts1 = get_now_seconds_local()
    for x in range(10000):
        add_sell_order_kraken(krak_key, "BCHXBT", price=0.5, amount=0.1, order_state=order_state[EXCHANGE.KRAKEN])
        sleep_for(30)

    ts2 = get_now_seconds_local()
    order_state = get_updated_order_state(order_state)
    print "Goal was to set 10000 deals: "
    print "Total number of open orders: ", len(order_state[EXCHANGE.KRAKEN].open_orders)
    print "It take ", ts2-ts1, " seconds"


def test_kraken_market_utils(krak_key):
    res = get_orders_kraken(krak_key)

    print res.get_total_num_of_orders()

    print res

    error_code, r = get_balance_kraken(krak_key)
    print r
    pol_key = get_key_by_exchange(EXCHANGE.POLONIEX)
    r = get_balance_poloniex(pol_key)
    print r
    bit_key = get_key_by_exchange(EXCHANGE.BITTREX)
    r = get_balance_bittrex(bit_key)
    print r
    add_buy_order_kraken(krak_key, "XETHXXBT", 0.07220, 0.02)
    add_sell_order_kraken(krak_key, "XETHXXBT", 0.07220, 0.02)
    add_sell_order_kraken(krak_key, "XETHXXBT", 0.07220, 0.02)

    cancel_order_kraken(krak_key, 'O6PGMG-DXKYV-UU4MNM')


def test_binance_market_utils():
    error_code, r = get_balance_binance(bin_key)
    print r
    error_code, r = add_buy_order_binance(bin_key, "RDNBTC", price=0.00022220, amount=10)
    print r

    error_code, r = add_sell_order_binance(bin_key, "RDNBTC", price=1.00022220, amount=1)
    error_code, r = cancel_order_binance(bin_key, "RDNBTC", 1373492)


def test_time_epoch():
    t = get_now_seconds_utc()
    t1 = get_now_seconds_local()
    t2 = generate_nonce()
    print "utc", t
    print "local", t1
    print "nonce", t2


@timecall
def get_ohlc_time_test():
    end_time = get_now_seconds_utc()
    start_time = end_time - 900

    get_ohlc(start_time, end_time)


@timecall
def get_ohlc_time_fast_test():
    end_time = get_now_seconds_utc()
    start_time = end_time - 900
    return get_ohlc_speedup(start_time, end_time)

# for x in range(100):
#     get_ohlc_time_test()


# res = get_ohlc_time_fast_test()
# for v in res:
#     print v

@timecall
def get_ticker_time_fast():
    timest = get_now_seconds_utc()
    processor = ConnectionPool()
    return get_ticker_speedup(timest, processor)


@timecall
def get_history_time_fast():
    end_time = get_now_seconds_utc()
    start_time = end_time - POLL_PERIOD_SECONDS
    processor = ConnectionPool()

    trade_history = get_history_speedup(start_time, end_time, processor)
    return trade_history


@timecall
def get_order_book_time_fast():
    end_time = get_now_seconds_utc()
    start_time = end_time - POLL_PERIOD_SECONDS
    processor = ConnectionPool()

    trade_history = get_order_book_speedup(start_time, end_time, processor)
    return trade_history


# for b in range(10):
#     get_ticker_time_fast()
# from core.base_analysis import compare_price, check_highest_bid_bigger_than_lowest_ask
# TRIGGER_THRESHOLD = 1.5 # 2 percents only

# processor = ConnectionPool()

# timest = get_now_seconds_utc()
# tickers = get_ticker_speedup(timest, processor)

# res = compare_price(tickers, TRIGGER_THRESHOLD, check_highest_bid_bigger_than_lowest_ask)

load_keys("./secret_keys")
krak_key = get_key_by_exchange(EXCHANGE.KRAKEN)
bin_key = get_key_by_exchange(EXCHANGE.BINANCE)
pol_key = get_key_by_exchange(EXCHANGE.POLONIEX)

er_code, res = get_orders_history_poloniex(pol_key, "all")
print res

