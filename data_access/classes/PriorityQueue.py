import redis as _redis
import pickle
from utils.time_utils import get_now_seconds_utc_ms


class PriorityQueue(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def add_order_to_watch_queue(self, topic_id, order):
        """
            Place orders to watch list = priority queue by TIME.
            We have to use current time instead of create time of orders to avoid collisions and overwrites.

        :param topic_id: Redis key
        :param order:
        :return:
        """
        return self.r.zadd(topic_id, get_now_seconds_utc_ms(), pickle.dumps(order))

    def first(self, topic_id):
        return self.r.zrevrange(topic_id, 0, 0)[0]

    def get_oldest_order(self, topic_id):
        try:
            _item = self.first(topic_id)
            while self.r.zrem(topic_id, _item) == 0:
                # Somebody else also got the same item and removed before us
                # Try again
                _item = self.first(topic_id)

            # We manager to pop the item from the queue
            return pickle.loads(_item)
        except IndexError:
            # Queue is empty
            pass

        return None
