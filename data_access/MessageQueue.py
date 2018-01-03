from data.BaseData import BaseData
from constants import CACHE_HOST, CACHE_PORT
import redis as _redis
from enums.notifications import NOTIFICATION

message_queue = None

ARBITRAGE_MSG = "ticker_alerts"
DEAL_INFO_MSG = "deal_alerts"
DEBUG_INFO_MSG = "debug_alerts"

QUEUE_TOPICS = [ARBITRAGE_MSG, DEAL_INFO_MSG, DEBUG_INFO_MSG]


def get_notification_id_by_topic_name(topic_name):
    return {
        ARBITRAGE_MSG: NOTIFICATION.ARBITRAGE,
        DEBUG_INFO_MSG: NOTIFICATION.DEBUG,
        DEAL_INFO_MSG: NOTIFICATION.DEAL
    }[topic_name]


class MessageQueue(BaseData):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def add_message(self, topic_id, msg):
        self.r.rpush(topic_id, msg)

    def get_topic_size(self, topic_id):
        return self.r.llen(topic_id)

    def empty(self, topic_id):
        return self.get_topic_size(topic_id) == 0

    def get_message(self, topic_id, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.r.blpop(topic_id, timeout=timeout)
        else:
            item = self.r.lpop(topic_id)

        if item:
            item = item[1]
        return item

    def get_message_nowait(self, topic_id):
        """Equivalent to get(False)."""
        return self.get_message(topic_id, False)


def connect_to_message_queue():
    global message_queue
    message_queue = MessageQueue(host=CACHE_HOST, port=CACHE_PORT)
    return message_queue


def get_message_queue():
    global message_queue
    if message_queue is None:
        return connect_to_message_queue()
    return message_queue