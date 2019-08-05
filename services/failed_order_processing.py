import argparse

from data_access.message_queue import get_message_queue, FAILED_ORDERS_MSG
from data_access.priority_queue import get_priority_queue
from data_access.memory_cache import get_cache

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for
from utils.key_utils import load_keys

from core.failed_order import process_failed_order
from services.common import process_args

from constants import HEARTBEAT_TIMEOUT


def process_failed_orders(args):
    """
                We try to address following issue

            Due to network issue or just bugs we may end up in situation that we are failed to place order
            Or we think so. Such orders registered in dedicated queue. We want to re-process them
            to minimise loss.

            Option 1: We managed to place order, just didn't get proper response from exchange
            - i.e. didn't wait enough for exchange to response
            Option 2: We managed to place order, just exchange were overloaded and decided to
            return to us some errors ()
            Option 3: We didn't managed to place order
                nonce issue - particular poloniex
                exchange issue - kraken
                ill fate - :(
            Option 4: ??? TODO

            First we try to find order in open or executed.
            In case we find it - update order_id in db.
            If it still open add it to watch list for expired orders processing.

            If not we can replace it by market with idea that there is high probability that other arbitrage deal were
            successfully placed

    :param args:
    :return:
    """

    pg_conn, settings = process_args(args)

    load_keys(settings.key_path)
    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)
    local_cache = get_cache(host=settings.cache_host, port=settings.cache_port)
    priority_queue = get_priority_queue(host=settings.cache_host, port=settings.cache_port)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Failed order processing service, constantly listen for new messages in failed orders queue.
    And try to correlate it with open or closed orders within exchange.
    In case it can't find - we try to close deal by market price.
    """)

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    process_failed_orders(arguments)
