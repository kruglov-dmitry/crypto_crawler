# coding=utf-8

from binance.buy_utils import add_buy_order_binance

from dao.deal_utils import init_deals_with_logging_speedy
from data.trade import Trade
from data.trade_pair import TradePair
from data.arbitrage_config import ArbitrageConfig
from data_access.classes.connection_pool import ConnectionPool

from enums.currency_pair import CURRENCY_PAIR
from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE

from poloniex.buy_utils import add_buy_order_poloniex
from poloniex.sell_utils import add_sell_order_poloniex

from utils.key_utils import load_keys, get_key_by_exchange
from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.currency_utils import get_currency_pair_name_by_exchange_id
from data_access.message_queue import get_message_queue
from data_access.priority_queue import ORDERS_EXPIRE_MSG, get_priority_queue


from dao.order_utils import get_open_orders_for_arbitrage_pair

from utils.debug_utils import LOG_ALL_DEBUG


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


def test_open_orders_retrieval_arbitrage():

    sell_exchange_id = EXCHANGE.BINANCE
    buy_exchange_id = EXCHANGE.POLONIEX
    pair_id = CURRENCY_PAIR.BTC_TO_OMG
    threshold = 2.0
    reverse_threshold = 2.0
    balance_threshold = 5.0
    deal_expire_timeout = 60
    logging_level = LOG_ALL_DEBUG

    cfg = ArbitrageConfig(sell_exchange_id, buy_exchange_id,
                          pair_id, threshold,
                          reverse_threshold, balance_threshold,
                          deal_expire_timeout,
                          logging_level)
    load_keys("./secret_keys")
    msg_queue1 = get_message_queue()
    processor = ConnectionPool(pool_size=2)
    print cfg
    res = get_open_orders_for_arbitrage_pair(cfg, processor)
    print "Length:", len(res)
    for r in res:
        print r


#
#       For testing new currency pair
#

def test_binance_xlm():
    load_keys("./secret_keys")
    key = get_key_by_exchange(EXCHANGE.BINANCE)
    pair_id = CURRENCY_PAIR.BTC_TO_XLM
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.BINANCE)
    err, json_repr = add_buy_order_binance(key, pair_name, price=0.00003000, amount=100)
    print json_repr


def test_poloniex_doge():
    load_keys("./secret_keys")
    key = get_key_by_exchange(EXCHANGE.POLONIEX)
    pair_id = CURRENCY_PAIR.BTC_TO_DGB
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.POLONIEX)
    err, json_repr = add_buy_order_poloniex(key, pair_name, price=0.00000300, amount=100)
    print json_repr


def test_new_sell_api():
    # STRAT vol 10 sell 0.0015 buy 0.0007

    load_keys("./secret_keys")
    key = get_key_by_exchange(EXCHANGE.POLONIEX)
    pair_id = CURRENCY_PAIR.BTC_TO_STRAT
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.POLONIEX)
    err, json_repr = add_buy_order_poloniex(key, pair_name, price=0.0007, amount=10)
    print json_repr
    err, json_repr = add_sell_order_poloniex(key, pair_name, price=0.0015, amount=10)
    print json_repr

    key = get_key_by_exchange(EXCHANGE.BITTREX)
    pair_id = CURRENCY_PAIR.BTC_TO_STRAT
    pair_name = get_currency_pair_name_by_exchange_id(pair_id, EXCHANGE.BITTREX)
    err, json_repr = add_buy_order_bittrex(key, pair_name, price=0.0007, amount=10)
    print json_repr
    err, json_repr = add_sell_order_bittrex(key, pair_name, price=0.0015, amount=10)
    print json_repr


def test_trade_methods_huobi():
    from huobi.currency_utils import get_currency_pair_to_huobi
    from huobi.order_utils import get_open_orders_huobi

    """
    Sell Zil 1000 штук по 0.00000620 - должно сработать
    Sell Zil 1000 по 0.00000750
    Buy Zil 1000 по 0.00000525
    :return:
    """

    load_keys("./secret_keys")
    key = get_key_by_exchange(EXCHANGE.HUOBI)
    pair_name = get_currency_pair_to_huobi(CURRENCY_PAIR.BTC_TO_VEN)

    # time_start = parse_time("2018-02-12 00:00:00", '%Y-%m-%d %H:%M:%S')
    # time_end = parse_time("2018-02-14 00:00:00", '%Y-%m-%d %H:%M:%S')

    # res, order_history = get_order_history_huobi(key, pair_name, time_start, time_end)
    # if len(order_history) > 0:
    #     for b in order_history:
    #         print b
    priority_queue = get_priority_queue()

    ts = get_now_seconds_utc()
    order = Trade(DEAL_TYPE.SELL, EXCHANGE.HUOBI, CURRENCY_PAIR.BTC_TO_ZIL,
                  price=0.00000750, volume=1000.0, order_book_time=ts, create_time=ts, execute_time=ts, order_id='whatever')
    # # order = Trade(DEAL_TYPE.BUY, EXCHANGE.HUOBI, CURRENCY_PAIR.BTC_TO_ZIL,
    # #               price=0.00000525, volume=1000.0,
    # #               order_book_time=ts, create_time=ts, execute_time=ts, order_id='whatever')
    # # order = Trade(DEAL_TYPE.SELL, EXCHANGE.HUOBI, CURRENCY_PAIR.BTC_TO_ZIL,
    # #               price=0.00000620, volume=1000.0,
    # #               order_book_time=ts, create_time=ts, execute_time=ts, order_id='whatever')

    # #### msg = "Testing huobi - {tt}".format(tt=order)
    # #### err_code, json_document = init_deal(order, msg)
    # #### print json_document
    # #### order.order_id = parse_order_id(order.exchange_id, json_document)
    # #### print "Parsed order_id: ", order.order_id
    priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)

    # # cancel_order_huobi(key, 'pair_name', '2915287415')
    # # cancel_order_huobi(key, 'pair_name', '2917275007')
    # # cancel_order_huobi(key, 'pair_name', '2934276449')
    # # cancel_order_huobi(key, 'pair_name', '2934368019')

    pair_name = get_currency_pair_to_huobi(CURRENCY_PAIR.BTC_TO_ZIL)

    res, open_orders = get_open_orders_huobi(key, pair_name)
    # print type(open_orders)
    for b in open_orders:
        print b, type(b)
    # # res, order_history = get_order_history_huobi(key, pair_name)
    # # for b in order_history:
    # #     print b

    """

    error_code, r = add_buy_order_binance(bin_key, "RDNBTC", price=0.00022220, amount=10)
    print r

    error_code, r = add_sell_order_binance(bin_key, "RDNBTC", price=1.00022220, amount=1)
    error_code, r = cancel_order_binance(bin_key, "RDNBTC", 1373492)
    """


def test_pool():
    def heavy_load():
        sleep_for(3)
        print "heavy_load"

    def more_heavy_load():
        sleep_for(30)
        print "WTF"

    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    import gevent
    from data_access.classes.connection_pool import ConnectionPool
    processor = ConnectionPool(10)

    iters = []
    for x in xrange(100):
        iters.append(x)

    for work_batch in batch(iters, 10):
        futures = []
        for x in work_batch:
            futures.append(processor.network_pool.spawn(more_heavy_load))
        gevent.joinall(futures)

    for work_batch in batch(iters, 10):
        futures = []
        for x in work_batch:
            futures.append(processor.network_pool.spawn(heavy_load))
        gevent.joinall(futures)


def compare_order_book():
    from huobi.order_book_utils import get_order_book_huobi
    import time
    from websocket import create_connection
    import zlib
    from huobi.currency_utils import get_currency_pair_to_huobi
    from utils.file_utils import log_to_file
    from data.order_book import OrderBook
    import json

    ws = None


    for pair_id in [CURRENCY_PAIR.BTC_TO_ETH]:
        pair_name = get_currency_pair_to_huobi(pair_id)
        if pair_name is None:
            print pair_id
            continue
        now_time = get_now_seconds_utc()
        order_book1 = get_order_book_huobi(pair_name, now_time)
        log_to_file(order_book1,"public_rest_api.txt")


    tradeStr="""{"sub": "market.ethbtc.depth.step0","id": "id10"}"""
    # tradeStr="""{{'sub': 'market.{pp}.depth.step0','id': 'id10'}}""".format(pp=pair_name)

    while(1):
        try:
            ws = create_connection("wss://api.huobipro.com/ws")
            break
        except:
            print('connect ws error,retry...')
            time.sleep(5)

    def process_result(compressData, tradeStr):
        result=zlib.decompress(compressData, 16+zlib.MAX_WBITS).decode('utf-8')
        if result[:7] == '{"ping"':
            ts=result[8:21]
            pong='{"pong":'+ts+'}'
            ws.send(pong)
            ws.send(tradeStr)

        return result

    ws.send(tradeStr)
    compressData = ws.recv()
    print "CONFIRMATION OF SUBSCRIPTION:", process_result(compressData, tradeStr)

    while True:
        compressData = ws.recv()
        json_repr = process_result(compressData, tradeStr)
        print "DELTA?", json_repr
        if "ping" not in json_repr:
            json_repr = json.loads(json_repr)
            order_book2 = OrderBook.from_huobi(json_repr["tick"], pair_name,get_now_seconds_utc())
            log_to_file(order_book2,"socket_api.txt")
            break

    compare_order_book()
