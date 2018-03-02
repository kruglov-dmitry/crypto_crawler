from data_access.message_queue import get_message_queue, FAILED_ORDERS_MSG
from data_access.priority_queue import get_priority_queue
from data_access.memory_cache import get_cache

from dao.db import init_pg_connection

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for
from utils.key_utils import load_keys

from core.failed_order import process_failed_order

from constants import HEARTBEAT_TIMEOUT


if __name__ == "__main__":

    # FIXME NOTE: read from config redis host \ port pass it to get_*_queue methods

    """
                We try to address following issue
                
            Due to network issue or just bugs we may end up in situation that we are failed to place order
                    Or we think so.
                    
            Option 1: We managed to place order, just didn't wait for exchange enough timeout
            Option 2: nonce issue - particular poloniex
            
            Option 3: ??? TODO
            
            First we try to find order in open or executed.
            In case we find it - update deal_id in db.
            If it still open add it to watch list for expired orders processing.
            
            If not we can replace it by market with idea that there is high probability that other arbitrage deal were 
            successfully placed
    """

    # FIXME NOTE - read settings from cfg!

    load_keys("./secret_keys")
    msg_queue = get_message_queue()
    local_cache = get_cache()
    priority_queue = get_priority_queue()

    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")

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
