from data_access.message_queue import get_message_queue, FAILED_ORDERS_MSG

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for


EXPIRATION_TIMEOUT = 15
HEARTBEAT_TIMEOUT = 60


if __name__ == "__main__":

    # FIXME NOTE: read from config redis host \ port pass it to get_*_queue methods

    """
                We try to address following issue
                
            Due to network issue or 
    """

    msg_queue = get_message_queue()
    cnt = 0

    while True:
        order = msg_queue.get_next_order(FAILED_ORDERS_MSG)
        if order is not None:
            print_to_console("Saving {o} in db".format(o=order), LOG_ALL_ERRORS)
        sleep_for(1)
        cnt += 1

        if cnt >= 60:
            cnt = 0
            print_to_console("Failed orders processing heartbeat", LOG_ALL_ERRORS)