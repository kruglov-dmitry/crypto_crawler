import argparse

from data_access.message_queue import ORDERS_MSG, get_message_queue

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for

from dao.db import save_order_into_pg

from constants import HEARTBEAT_TIMEOUT

from services.common import process_args


def process_placed_orders(args):
    """
            Check for new orders placed by ANY of trading bots


    :param args:
    :return:
    """
    pg_conn, settings = process_args(args)

    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)

    cnt = 0

    while True:
        order = msg_queue.get_next_order(ORDERS_MSG)
        if order is not None:
            save_order_into_pg(order, pg_conn)
            print_to_console("Saving {} in db".format(order), LOG_ALL_ERRORS)
        sleep_for(1)
        cnt += 1

        if cnt >= HEARTBEAT_TIMEOUT:
            cnt = 0
            print_to_console("Order storing heartbeat", LOG_ALL_ERRORS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
      Order saving - every second check message queue for new orders issued by bot processes and save them to postgres.""")

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    process_placed_orders(arguments)
