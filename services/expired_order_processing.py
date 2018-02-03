from data_access.message_queue import get_message_queue
from data_access.priority_queue import ORDERS_EXPIRE_MSG, get_priority_queue

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for, get_now_seconds_utc

from core.expired_deal import process_expired_order


EXPIRATION_TIMEOUT = 15
HEARTBEAT_TIMEOUT = 60


if __name__ == "__main__":

    # FIXME NOTE: read from config redis host \ port pass it to get_*_queue methods

    msg_queue = get_message_queue()
    priority_queue = get_priority_queue()
    cnt = 0

    while True:
        curr_ts = get_now_seconds_utc()

        order = priority_queue.get_oldest_order(ORDERS_EXPIRE_MSG)
        if order is not None:
            order_age = curr_ts - order.create_time
            if order_age < EXPIRATION_TIMEOUT:
                sleep_for(EXPIRATION_TIMEOUT - order_age)
            process_expired_order(order, msg_queue, priority_queue)
        else:
            print_to_console("Watch list is empty sleeping", LOG_ALL_ERRORS)
            sleep_for(1)
