from data_access.message_queue import get_message_queue
from data_access.priority_queue import ORDERS_EXPIRE_MSG, get_priority_queue
from data_access.memory_cache import get_cache

from debug_utils import print_to_console, LOG_ALL_ERRORS, EXPIRED_ORDER_PROCESSING_FILE_NAME
from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.key_utils import load_keys
from utils.file_utils import log_to_file

from core.expired_deal import process_expired_order

EXPIRATION_TIMEOUT = 15
HEARTBEAT_TIMEOUT = 60


if __name__ == "__main__":

    # FIXME NOTE: read from config redis host \ port pass it to get_*_queue methods
    load_keys("./secret_keys")
    msg_queue = get_message_queue()
    priority_queue = get_priority_queue()
    local_cache = get_cache()

    cnt = 0

    while True:
        curr_ts = get_now_seconds_utc()

        order = priority_queue.get_oldest_order(ORDERS_EXPIRE_MSG)
        if order is not None:
            msg = "Current expired order - {o}".format(o=order)
            log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)
            order_age = curr_ts - order.create_time
            if order_age < EXPIRATION_TIMEOUT:
                msg = "A bit early - {t1} {t2} WILLL SLEEP".format(t1=order_age, t2=EXPIRATION_TIMEOUT)
                log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)
                sleep_for(EXPIRATION_TIMEOUT - order_age)

            process_expired_order(order, msg_queue, priority_queue, local_cache)
        else:
            print_to_console("Watch list is empty sleeping", LOG_ALL_ERRORS)
            log_to_file("Watch list is empty sleeping", EXPIRED_ORDER_PROCESSING_FILE_NAME)
            sleep_for(1)
