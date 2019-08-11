import argparse

from deploy.classes.common_settings import CommonSettings

from data_access.priority_queue import ORDERS_EXPIRE_MSG

from utils.debug_utils import print_to_console, LOG_ALL_ERRORS, EXPIRED_ORDER_PROCESSING_FILE_NAME, \
    set_log_folder, set_logging_level
from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.key_utils import load_keys
from utils.file_utils import log_to_file
from utils.args_utils import init_queues

from core.expired_order import process_expired_order
from constants import HEARTBEAT_TIMEOUT, ORDER_EXPIRATION_TIMEOUT


def process_expired_orders(args):
    """

    :param args: file name
    :return:
    """
    settings = CommonSettings.from_cfg(args.cfg)
    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    load_keys(settings.key_path)

    priority_queue, msg_queue, local_cache = init_queues(settings)

    cnt = 0

    while True:
        curr_ts = get_now_seconds_utc()

        order = priority_queue.get_oldest_order(ORDERS_EXPIRE_MSG)

        if order:
            msg = "Current expired order - {}".format(order)
            log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)
            order_age = curr_ts - order.create_time
            if order_age < ORDER_EXPIRATION_TIMEOUT:
                msg = "A bit early - {t1} {t2} WILLL SLEEP".format(t1=order_age, t2=ORDER_EXPIRATION_TIMEOUT)
                log_to_file(msg, EXPIRED_ORDER_PROCESSING_FILE_NAME)
                sleep_for(ORDER_EXPIRATION_TIMEOUT - order_age)

            process_expired_order(order, msg_queue, priority_queue, local_cache)

        sleep_for(1)
        cnt += 1

        if cnt >= HEARTBEAT_TIMEOUT:
            cnt = 0
            print_to_console("Watch list is empty sleeping", LOG_ALL_ERRORS)
            log_to_file("Watch list is empty sleeping", EXPIRED_ORDER_PROCESSING_FILE_NAME)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Expired order processing service, constantly listen for new messages in expired orders queue.
    Order considered expired in case it doesn't closed for more then {EXPIRATION_TIMEOUT} seconds.
    """.format(EXPIRATION_TIMEOUT=ORDER_EXPIRATION_TIMEOUT))

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    process_expired_orders(arguments)
