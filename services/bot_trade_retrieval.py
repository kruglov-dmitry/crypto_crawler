import argparse

from logging.balance_monitoring_logging import log_initial_settings

from utils.key_utils import load_keys
from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.exchange_utils import parse_exchange_ids
from deploy.classes.CommonSettings import CommonSettings

from analysis.data_load_for_profit_report import get_trade_retrieval_method_by_exchange

from debug_utils import set_logging_level, set_log_folder
from utils.time_utils import parse_time

from dao.db import init_pg_connection

POLL_TIMEOUT = 900


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
    Trade retrieval service, every {POLL_TIMEOUT} for configured via:
        --exchanges_ids comma-separated list of exchange names. 
        --start_time - start of time interval
        --end_time - end of time interval """.format(POLL_TIMEOUT=POLL_TIMEOUT))

    parser.add_argument('--exchanges', action='store', required=True)
    parser.add_argument('--cfg', action='store', required=True)

    parser.add_argument('--start_time', action="store", type=int)
    parser.add_argument('--end_time', action="store", type=int)

    arguments = parser.parse_args()

    exchanges_ids = parse_exchange_ids(arguments.exchanges)
    log_initial_settings("Starting trade history retrieval for bots using following exchanges: \n", exchanges_ids)

    settings = CommonSettings.from_cfg(arguments.cfg)

    if arguments.start_time is None or arguments.end_time is None:
        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_TIMEOUT
    else:
        end_time = parse_time(arguments.end_time, '%Y-%m-%d %H:%M:%S')
        start_time = parse_time(arguments.start_time, '%Y-%m-%d %H:%M:%S')

    if start_time == end_time or end_time <= start_time:
        print "Wrong time interval provided! {ts0} - {ts1}".format(ts0=start_time, ts1=end_time)
        assert False

    load_keys(settings.key_path)

    pg_conn = init_pg_connection(_db_host=settings.db_host,
                                 _db_port=settings.db_port,
                                 _db_name=settings.db_name)

    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    while True:
        for exchange_id in exchanges_ids:
            method = get_trade_retrieval_method_by_exchange(exchange_id)
            method(pg_conn, start_time, end_time)

        print "Trade retrieval hearbeat"

        sleep_for(POLL_TIMEOUT)

        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_TIMEOUT
