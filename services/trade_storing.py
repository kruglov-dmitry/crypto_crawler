from data_access.message_queue import ORDERS_MSG, get_message_queue
from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for
from dao.db import init_pg_connection, save_order_into_pg


if __name__ == "__main__":

    # FIXME NOTE - read settings from cfg!

    msg_queue = get_message_queue()
    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")
    cnt = 0

    while True:
        order = msg_queue.get_next_order(ORDERS_MSG)
        if order is not None:
            save_order_into_pg(order, pg_conn)
            print_to_console("Saving {o} in db".format(o=order), LOG_ALL_ERRORS)
        sleep_for(1)
        cnt += 1

        if cnt >= 60:
            cnt = 0
            print_to_console("Trade storing heartbeat", LOG_ALL_ERRORS)
