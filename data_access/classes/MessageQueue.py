from data.BaseData import BaseData
import redis as _redis
import pickle
from utils.time_utils import get_now_seconds_utc_ms


class MessageQueue(BaseData):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def add_message(self, topic_id, msg):
        msg = msg + "\nTS: " + str(get_now_seconds_utc_ms())
        self.r.rpush(topic_id, msg)

    def get_topic_size(self, topic_id):
        return self.r.llen(topic_id)

    def empty(self, topic_id):
        return self.get_topic_size(topic_id) == 0

    def get_message(self, topic_id, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        # if block:
        #     item = self.r.blpop(topic_id, timeout=timeout)
        # else:
        #     item = self.r.lpop(topic_id)

        # if item:
        #     item = item[1]
        item = self.r.lpop(topic_id)
        return item

    def get_message_nowait(self, topic_id):
        """Equivalent to get(False)."""
        return self.get_message(topic_id, True)

    def add_message_to_start(self, topic_id, msg):
        self.r.lpush(topic_id, msg)

    def add_order(self, topic_id, balance):
        self.r.lpush(topic_id, pickle.dumps(balance))

    def get_next_order(self, topic_id):
        return pickle.loads(self.get_message(topic_id, True))
