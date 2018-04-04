from collections import defaultdict, Counter
import sys
import ConfigParser

from dao.db import init_pg_connection

from utils.key_utils import load_keys
from utils.time_utils import parse_time
from debug_utils import set_log_folder
from utils.currency_utils import split_currency_pairs

from analysis.data_load_for_profit_report import fetch_trades_history_to_db

from analysis.grouping_utils import group_trades_by_orders
from analysis.data_preparation import prepare_data
from analysis.profit_report_analysis import compute_loss, compute_profit_by_pair, save_report
from analysis.classes.ProfitDetails import ProfitDetails


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: {prg_name} your_config.cfg".format(prg_name=sys.argv[0])
        print "FIXME TODO: we should use argparse module"
        exit(0)

    cfg_file_name = sys.argv[1]

    config = ConfigParser.RawConfigParser()
    config.read(cfg_file_name)

    db_host = config.get("postgres", "db_host")
    db_port = config.get("postgres", "db_port")
    db_name = config.get("postgres", "db_name")

    should_fetch_history_to_db = config.getboolean("profit_report", "fetch_history_from_exchanges")
    fetch_from_start = config.getboolean("profit_report", "fetch_from_start")

    start_time = parse_time(config.get("profit_report", "start_time"), '%Y-%m-%d %H:%M:%S')
    end_time = parse_time(config.get("profit_report", "end_time"), '%Y-%m-%d %H:%M:%S')

    if start_time == end_time or end_time <= start_time:
        print "Wrong time interval provided! {ts0} - {ts1}".format(ts0=start_time, ts1=end_time)
        assert False

    pg_conn = init_pg_connection(_db_host=db_host, _db_port=db_port, _db_name=db_name)

    key_path = config.get("keys", "path_to_api_keys")
    log_folder = config.get("logging_tools", "logs_folder")
    load_keys(key_path)
    set_log_folder(log_folder)

    if should_fetch_history_to_db:
        fetch_trades_history_to_db(pg_conn, start_time, end_time, fetch_from_start)

    orders, history_trades = prepare_data(pg_conn, start_time, end_time)

    missing_orders, failed_orders, orders_with_trades = group_trades_by_orders(orders, history_trades)

    # 2 stage - bucketing all that crap by pair_id
    trades_to_order = defaultdict(list)
    for order, trade_list in orders_with_trades:
        trades_to_order[order.pair_id].append((order, trade_list))

    total_profit_by_base = Counter()
    profit_details = defaultdict(list)

    for pair_id in trades_to_order:
        profit_pair, profit_base = compute_profit_by_pair(pair_id, trades_to_order[pair_id])
        base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

        total_profit_by_base[base_currency_id] += profit_base

        profit_details[base_currency_id].append(
            ProfitDetails(base_currency_id, dst_currency_id, pair_id, profit_pair, profit_base)
        )

    loss_details, total_loss_by_base = compute_loss(orders_with_trades)

    save_report(start_time, end_time, total_profit_by_base, profit_details,
                missing_orders, failed_orders, loss_details, total_loss_by_base,
                orders, history_trades
                )
