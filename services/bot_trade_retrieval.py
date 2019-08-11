import argparse

from logging_tools.balance_monitoring_logging import log_initial_settings

from analysis.data_load_for_profit_report import get_trade_retrieval_method_by_exchange

from utils.debug_utils import print_to_console, LOG_ALL_DEBUG
from utils.time_utils import sleep_for, get_now_seconds_utc, parse_time
from utils.key_utils import load_keys
from utils.system_utils import die_hard

from utils.args_utils import process_args

TRADE_POLL_TIMEOUT = 900


def load_trade_history(args):
    """
        Retrieve executed trades from ALL exchanges via REST api
        and save into db

        Those data later will be used for analysis
        of profitability of trading and bot's performance

    :param args: period, exchanges, connection details
    :return:
    """

    pg_conn, settings = process_args(args)

    log_initial_settings("Starting trade history retrieval for bots using following exchanges: \n", settings.exchanges)

    if args.start_time is None or args.end_time is None:
        end_time = get_now_seconds_utc()
        start_time = end_time - 24 * 3600
    else:
        end_time = parse_time(args.end_time, '%Y-%m-%d %H:%M:%S')
        start_time = parse_time(args.start_time, '%Y-%m-%d %H:%M:%S')

    if start_time == end_time or end_time <= start_time:
        die_hard("Wrong time interval provided! {ts0} - {ts1}".format(ts0=start_time, ts1=end_time))

    load_keys(settings.key_path)

    while True:
        for exchange_id in settings.exchanges:
            method = get_trade_retrieval_method_by_exchange(exchange_id)
            method(pg_conn, start_time, end_time)
            sleep_for(1)

        print_to_console("Trade retrieval heartbeat", LOG_ALL_DEBUG)

        sleep_for(TRADE_POLL_TIMEOUT)

        end_time = get_now_seconds_utc()
        start_time = end_time - 24 * 3600
        # start_time = end_time - POLL_TIMEOUT


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
    Trade retrieval service, every {POLL_TIMEOUT} for configured via:
        --start_time - start of time interval
        --end_time - end of time interval """.format(POLL_TIMEOUT=TRADE_POLL_TIMEOUT))

    parser.add_argument('--cfg', action='store', required=True)

    parser.add_argument('--start_time', action="store", type=int)
    parser.add_argument('--end_time', action="store", type=int)

    arguments = parser.parse_args()

    load_trade_history(arguments)
