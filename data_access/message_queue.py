from data_access.classes.message_queue import MessageQueue
from constants import CACHE_PORT, CACHE_HOST
from enums.notifications import NOTIFICATION


MESSAGE_QUEUE = None

ARBITRAGE_MSG = "ticker_alerts"
DEAL_INFO_MSG = "deal_alerts"
DEBUG_INFO_MSG = "debug_alerts"
ORDERS_MSG = "orders"
FAILED_ORDERS_MSG = "failed_orders"

QUEUE_TOPICS = [ARBITRAGE_MSG, DEAL_INFO_MSG, DEBUG_INFO_MSG]


def get_notification_id_by_topic_name(topic_name):
    return {
        ARBITRAGE_MSG: NOTIFICATION.ARBITRAGE,
        DEBUG_INFO_MSG: NOTIFICATION.DEBUG,
        DEAL_INFO_MSG: NOTIFICATION.DEAL
    }[topic_name]


def connect_to_message_queue(host=CACHE_HOST, port=CACHE_PORT):
    global MESSAGE_QUEUE
    MESSAGE_QUEUE = MessageQueue(host, port)
    return MESSAGE_QUEUE


def get_message_queue(host=CACHE_HOST, port=CACHE_PORT):
    if MESSAGE_QUEUE is None:
        return connect_to_message_queue(host, port)
    return MESSAGE_QUEUE
