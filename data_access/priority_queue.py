from data_access.classes.PriorityQueue import PriorityQueue
from constants import CACHE_PORT, CACHE_HOST

ORDERS_EXPIRE_MSG = "orders_watch_list"
priority_queue = None


def connect_to_priority_queue():
    global priority_queue
    priority_queue = PriorityQueue(host=CACHE_HOST, port=CACHE_PORT)
    return priority_queue


def get_priority_queue():
    global priority_queue
    if priority_queue is None:
        return connect_to_priority_queue()
    return priority_queue