from deploy.classes.CommonSettings import CommonSettings
from data_access.message_queue import get_message_queue, FAILED_ORDERS_MSG
from data_access.priority_queue import get_priority_queue
from data_access.memory_cache import get_cache

from dao.db import init_pg_connection

from debug_utils import print_to_console, LOG_ALL_ERRORS, set_logging_level, set_log_folder
from utils.time_utils import sleep_for
from utils.key_utils import load_keys

from core.failed_order import process_failed_order

from constants import HEARTBEAT_TIMEOUT
import argparse

"""
                We try to address following issue

            Due to network issue or just bugs we may end up in situation that we are failed to place order
                    Or we think so.

            Option 1: We managed to place order, just didn't wait for exchange enough timeout
            Option 2: nonce issue - particular poloniex

            Option 3: ??? TODO

            First we try to find order in open or executed.
            In case we find it - update order_id in db.
            If it still open add it to watch list for expired orders processing.

            If not we can replace it by market with idea that there is high probability that other arbitrage deal were 
            successfully placed
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Failed order processing service, constantly listen for new messages in failed orders queue.
    And try to correlate it with open or closed orders within exchange.
    In case it can't find - we try to make deal by market price.
    """)

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    load_keys(settings.key_path)
    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)
    local_cache = get_cache(host=settings.cache_host, port=settings.cache_port)
    priority_queue = get_priority_queue(host=settings.cache_host, port=settings.cache_port)
    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    pg_conn = init_pg_connection(_db_host=settings.db_host,
                                 _db_port=settings.db_port,
                                 _db_name=settings.db_name)

    cnt = 0

    while True:
        order = msg_queue.get_next_order(FAILED_ORDERS_MSG)
        if order is not None:
            process_failed_order(order, msg_queue, priority_queue, local_cache, pg_conn)

        sleep_for(1)
        cnt += 1

        if cnt >= HEARTBEAT_TIMEOUT:
            cnt = 0
            print_to_console("Failed orders processing heartbeat", LOG_ALL_ERRORS)
