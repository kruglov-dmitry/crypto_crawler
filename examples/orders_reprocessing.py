from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for

from data.trade import Trade

from data_access.message_queue import get_message_queue, FAILED_ORDERS_MSG
from data_access.priority_queue import get_priority_queue, ORDERS_EXPIRE_MSG

from dao.deal_utils import init_deal
from dao.dao import parse_order_id

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from enums.currency_pair import CURRENCY_PAIR

from constants import API_KEY_PATH


def test_failed_order_placement_huobi():

    load_keys(API_KEY_PATH)

    ts = get_now_seconds_utc()
    order = Trade(DEAL_TYPE.SELL, EXCHANGE.HUOBI, CURRENCY_PAIR.BTC_TO_ZIL,
                  price=0.00000750, volume=1000.0, order_book_time=ts, create_time=ts)

    msg = "Testing huobi - {tt}".format(tt=order)
    err_code, json_document = init_deal(order, msg)
    print json_document

    msg_queue = get_message_queue()
    msg_queue.add_order(FAILED_ORDERS_MSG, order)


def test_failed_order_placement_bittrex():
    load_keys(API_KEY_PATH)

    ts = get_now_seconds_utc()
    order = Trade(DEAL_TYPE.SELL, EXCHANGE.BITTREX, CURRENCY_PAIR.BTC_TO_ETH,
                  price=0.075, volume=0.1, order_book_time=ts, create_time=ts)

    msg = "Testing huobi - {tt}".format(tt=order)
    err_code, json_document = init_deal(order, msg)
    print json_document

    msg_queue = get_message_queue()
    msg_queue.add_order(FAILED_ORDERS_MSG, order)


def test_expired_deal_placement():
    load_keys(API_KEY_PATH)
    priority_queue = get_priority_queue()
    ts = get_now_seconds_utc()
    order = Trade(DEAL_TYPE.SELL, EXCHANGE.BINANCE, CURRENCY_PAIR.BTC_TO_STRAT, price=0.001, volume=5.0,
                  order_book_time=ts, create_time=ts, execute_time=ts, order_id='whatever')

    msg = "Replace existing order with new one - {tt}".format(tt=order)
    err_code, json_document = init_deal(order, msg)
    print json_document
    order.order_id = parse_order_id(order.exchange_id, json_document)
    priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, order)


def test_failed_deal_placement():
    load_keys(API_KEY_PATH)
    msg_queue = get_message_queue()
    ts = 1517938516
    order = Trade(DEAL_TYPE.SELL, EXCHANGE.BITTREX, CURRENCY_PAIR.BTC_TO_STRAT, price=0.000844, volume=5.0,
                  order_book_time=ts, create_time=ts, execute_time=ts, order_id=None)

    #   from dao.order_utils import get_open_orders_by_exchange
    #   r = get_open_orders_by_exchange(EXCHANGE.BITTREX, CURRENCY_PAIR.BTC_TO_STRAT)

    #   for rr in r:
    #       print r

    #   raise
    #
    # msg = "Replace existing order with new one - {tt}".format(tt=order)
    # err_code, json_document = init_deal(order, msg)
    # print json_document
    # order.deal_id = parse_deal_id(order.exchange_id, json_document)

    # msg_queue.add_order(ORDERS_MSG, order)
    sleep_for(3)
    msg_queue.add_order(FAILED_ORDERS_MSG, order)
    print order
