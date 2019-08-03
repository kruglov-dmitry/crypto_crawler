from data_access.message_queue import ORDERS_MSG, get_message_queue
from debug_utils import print_to_console, LOG_ALL_ERRORS, set_log_folder, set_logging_level
from utils.time_utils import sleep_for
from dao.db import init_pg_connection, save_order_into_pg

from constants import HEARTBEAT_TIMEOUT
import argparse
from deploy.classes.common_settings import CommonSettings

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
      Telegram notifier service - every second check message queue for new messages and sent them via bot interface.""")

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)
    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)
    pg_conn = init_pg_connection(_db_host=settings.db_host,
                                 _db_port=settings.db_port,
                                 _db_name=settings.db_name)
    cnt = 0

    while True:
        order = msg_queue.get_next_order(ORDERS_MSG)
        if order is not None:
            save_order_into_pg(order, pg_conn)
            print_to_console("Saving {o} in db".format(o=order), LOG_ALL_ERRORS)
        sleep_for(1)
        cnt += 1

        if cnt >= HEARTBEAT_TIMEOUT:
            cnt = 0
            print_to_console("Order storing heartbeat", LOG_ALL_ERRORS)
