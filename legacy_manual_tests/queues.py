from data_access.message_queue import get_message_queue, DEAL_INFO_MSG, ARBITRAGE_MSG, \
    DEBUG_INFO_MSG, ORDERS_MSG, FAILED_ORDERS_MSG
from data_access.priority_queue import get_priority_queue
from data_access.telegram_notifications import send_single_message
from enums.notifications import NOTIFICATION


def test_send_message_weird_symbols():
    msg = """My message contains some weird symbols - <Response> 
    [400] Json: {u'msg': u'Market is closed.', u'code': -1013} """
    send_single_message(msg, NOTIFICATION.DEAL)


def test_sorted_queue():
    priority_queue = get_priority_queue(host="192.168.1.106")
    priority_queue.add_order_to_watch_queue("YOPITOK", "First")
    priority_queue.add_order_to_watch_queue("YOPITOK", "Second")
    priority_queue.add_order_to_watch_queue("YOPITOK", "Third")
    priority_queue.add_order_to_watch_queue("YOPITOK", "fourth")
    priority_queue.add_order_to_watch_queue("YOPITOK", "Fives")
    priority_queue.add_order_to_watch_queue("YOPITOK", "Sixest")

    order = priority_queue.get_oldest_order("YOPITOK")
    while order is not None:
        print order
        order = priority_queue.get_oldest_order("YOPITOK")


def test_message_queue():
    msg_queue = get_message_queue()
    msg_queue.add_message(DEAL_INFO_MSG, "DEAL_INFO_MSG: Test DEAL_INFO_MSG")
    msg_queue.add_message(ARBITRAGE_MSG, "ARBITRAGE_MSG: Test ARBITRAGE_MSG")
    msg_queue.add_message(DEBUG_INFO_MSG, "DEBUG_INFO_MSG: Test DEBUG_INFO_MSG")
    msg_queue.add_message(ORDERS_MSG, "ORDERS_MSG: Test ORDERS_MSG")
    msg_queue.add_message(FAILED_ORDERS_MSG, "ORDERS_MSG: Test FAILED_ORDERS_MSG")
