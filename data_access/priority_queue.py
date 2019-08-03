from data_access.classes.priority_queue import PriorityQueue
from constants import CACHE_PORT, CACHE_HOST

ORDERS_EXPIRE_MSG = "orders_watch_list"
PRIORITY_QUEUE = None


def connect_to_priority_queue(host=CACHE_HOST, port=CACHE_PORT):
    global PRIORITY_QUEUE
    PRIORITY_QUEUE = PriorityQueue(host, port)
    return PRIORITY_QUEUE


def get_priority_queue(host=CACHE_HOST, port=CACHE_PORT):
    if PRIORITY_QUEUE is None:
        return connect_to_priority_queue(host, port)
    return PRIORITY_QUEUE
