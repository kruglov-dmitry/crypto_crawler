import argparse

from data_access.message_queue import get_message_queue
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_id_by_name, get_exchange_name_by_id
from services.balance_monitoring_logging import log_wrong_exchange_id

from utils.key_utils import load_keys
from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.file_utils import log_to_file

from analysis.data_load_for_profit_report import get_trade_retrieval_method_by_exchange

from debug_utils import print_to_console, LOG_ALL_ERRORS

from dao.db import init_pg_connection

POLL_TIMEOUT = 900


def log_initial_settings(exchanges_ids):
    msg = "Starting trade history retrieval for bots using following exchanges: \n"
    for exchange_id in exchanges_ids:
        msg += str(exchange_id) + " - " + get_exchange_name_by_id(exchange_id) + "\n"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, "balance.log")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Trade retrieval service, every {POLL_TIMEOUT} for configured via "
                                                 "--exchanges_ids comma-separated list of exchange names ".format(POLL_TIMEOUT=POLL_TIMEOUT))

    parser.add_argument('--exchanges', action='store', required=True)

    results = parser.parse_args()

    ids_list = [x.strip() for x in results.exchanges.split(',') if x.strip()]

    exchanges_ids = []
    for exchange_name in ids_list:
        new_exchange_id = get_exchange_id_by_name(exchange_name)
        if new_exchange_id in EXCHANGE.values():
            exchanges_ids.append(new_exchange_id)
        else:
            log_wrong_exchange_id(new_exchange_id)

            assert new_exchange_id in EXCHANGE.values()

    log_initial_settings(exchanges_ids)

    # FIXME NOTE - read settings from cfg!

    load_keys("./secret_keys")

    msg_queue = get_message_queue()
    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")

    cnt = 0

    while True:
        # We load initial balance using init_balance
        sleep_for(POLL_TIMEOUT)

        cnt += POLL_TIMEOUT

        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_TIMEOUT

        for exchange_id in exchanges_ids:
            method = get_trade_retrieval_method_by_exchange(exchange_id)
            method(pg_conn, start_time, end_time)

        print "Trade retrieval hearbeat"

