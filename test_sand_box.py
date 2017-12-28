from profilehooks import timecall

from binance.constants import BINANCE_CURRENCY_PAIRS
from binance.market_utils import cancel_order_binance
from binance.ohlc_utils import get_ohlc_binance
from binance.order_book_utils import get_order_book_binance
from binance.ticker_utils import get_tickers_binance
from binance.sell_utils import add_sell_order_binance
from binance.buy_utils import add_buy_order_binance
from binance.balance_utils import get_balance_binance
from binance.order_utils import get_open_orders_binance

from bittrex.market_utils import cancel_order_bittrex
from bittrex.balance_utils import get_balance_bittrex
from bittrex.buy_utils import add_buy_order_bittrex
from bittrex.sell_utils import add_sell_order_bittrex
from bittrex.order_utils import get_open_orders_bittrix

from poloniex.market_utils import get_orders_history_poloniex
from poloniex.market_utils import cancel_order_poloniex
from poloniex.balance_utils import get_balance_poloniex
from poloniex.buy_utils import add_buy_order_poloniex
from poloniex.sell_utils import add_sell_order_poloniex
from poloniex.order_utils import get_open_orders_poloniex

from kraken.market_utils import cancel_order_kraken
from kraken.balance_utils import get_balance_kraken
from kraken.buy_utils import add_buy_order_kraken
from kraken.sell_utils import add_sell_order_kraken
from kraken.order_utils import get_orders_kraken, get_open_orders_kraken


from enums.deal_type import DEAL_TYPE
from data.Trade import Trade
from data.TradePair import TradePair
from core.arbitrage_core import init_deals_with_logging_speedy
from enums.currency_pair import CURRENCY_PAIR

from core.arbitrage_core import dummy_order_state_init
from dao.dao import get_updated_order_state
from dao.history_utils import get_history_speedup

from data_access.memory_cache import generate_nonce
from dao.ohlc_utils import get_ohlc_speedup, get_ohlc
from dao.order_book_utils import get_order_book_speedup
from dao.ticker_utils import get_ticker_speedup
from data_access.ConnectionPool import ConnectionPool
from enums.currency import CURRENCY
from enums.exchange import EXCHANGE

from utils.key_utils import load_keys, get_key_by_exchange
from utils.time_utils import sleep_for, get_now_seconds_utc, get_now_seconds_local

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
        # add_sell_order_kraken_till_the_end(krak_key, "BCHXBT", price=0.5, amount=0.1, order_state=order_state[EXCHANGE.KRAKEN])
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
    """add_buy_order_kraken_try_till_the_end(krak_key, "XETHXXBT", 0.07220, 0.02)
    add_sell_order_kraken_till_the_end(krak_key, "XETHXXBT", 0.07220, 0.02)
    add_sell_order_kraken_till_the_end(krak_key, "XETHXXBT", 0.07220, 0.02)
    """
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
    processor = ConnectionPool()
    end_time = get_now_seconds_utc()
    start_time = end_time - 900
    return get_ohlc_speedup(start_time, end_time, processor)


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


def check_order_polonie(pol_key):
    er_code, res = get_orders_history_poloniex(pol_key, "all")
    print res

def check_deal_placements():
    create_time = get_now_seconds_utc()
    fake_order_book_time1 = -10
    fake_order_book_time2 = -20
    deal_volume = 5
    deal_price = -1
    pair_id = CURRENCY_PAIR.BTC_TO_ARDR

    sell_exchange_id = EXCHANGE.POLONIEX
    buy_exchange_id = EXCHANGE.BITTREX

    difference = "difference is HUGE"
    file_name = "test.log"

    processor = ConnectionPool(pool_size=2)

    trade_at_first_exchange = Trade(DEAL_TYPE.SELL, sell_exchange_id, pair_id,
                                    0.00000001, deal_volume, fake_order_book_time1,
                                    create_time)

    trade_at_second_exchange = Trade(DEAL_TYPE.BUY, buy_exchange_id, pair_id,
                                     0.00004, deal_volume, fake_order_book_time2,
                                     create_time)

    trade_pairs = TradePair(trade_at_first_exchange, trade_at_second_exchange, fake_order_book_time1, fake_order_book_time2, DEAL_TYPE.DEBUG)

    init_deals_with_logging_speedy(trade_pairs, difference, file_name, processor)


def check_open_order_retrieval():
    load_keys("./secret_keys")
    krak_key = get_key_by_exchange(EXCHANGE.KRAKEN)
    bin_key = get_key_by_exchange(EXCHANGE.BINANCE)
    pol_key = get_key_by_exchange(EXCHANGE.POLONIEX)
    bittrex_key = get_key_by_exchange(EXCHANGE.BITTREX)

    # err_code, res = get_open_orders_binance(bin_key, "XMRBTC")
    # for r in res:
    #     print r

    # err_code, res = get_open_orders_bittrix(bittrex_key, None)
    # for r in res:
    #     print r

    # err_code, res = get_open_orders_kraken(krak_key, None)
    # for r in res:
    #     print r

    err_code, res = get_open_orders_poloniex(pol_key, "BTC_ARDR")
    for r in res:
        print r


check_open_order_retrieval()
