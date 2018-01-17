import csv

from data.Trade import Trade

from dao.db import init_pg_connection, get_all_orders
from enums.exchange import EXCHANGE

from utils.key_utils import load_keys, get_key_by_exchange
from utils.time_utils import get_now_seconds_utc

from poloniex.market_utils import get_order_history_for_time_interval_poloniex
from bittrex.market_utils import get_order_history_for_time_interval_bittrex
from binance.market_utils import get_order_history_for_time_interval_binance, get_trades_history_binance
from binance.constants import BINANCE_CURRENCY_PAIRS


def save_to_csv_file(file_name, fields_list, array_list):

    with open(file_name, 'w') as f:
        writer = csv.writer(f, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fields_list)
        for cdr in array_list:
            writer.writerow(list(cdr))


if __name__ == "__main__":
    load_keys("./secret_keys")

    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")

    # orders = get_all_orders(pg_conn)

    # save_to_csv_file("tst.csv", Trade.get_fields(), orders)
    now_time = get_now_seconds_utc()
    two_days_ago = now_time - 2 * 24 * 60 * 60

    """key = get_key_by_exchange(EXCHANGE.POLONIEX)
    error_code, json_document = get_order_history_for_time_interval_poloniex(key, pair_name='all',
                                                                             time_start=two_days_ago,
                                                                             time_end=now_time, limit=10000)

    poloniex_orders = []
    for pair_name in json_document:
        for entry in json_document[pair_name]:
            poloniex_orders.append(Trade.from_poloniex_history(entry, pair_name))

    # save_to_csv_file("poloniex.csv", Trade.get_fields(), res)
    """

    """
    key = get_key_by_exchange(EXCHANGE.BITTREX)
    error_code, json_document = get_order_history_for_time_interval_bittrex(key, pair_name='all')

    bittrex_order = []
    for entry in json_document["result"]:
        bittrex_order.append(Trade.from_bittrex_history(entry))

    save_to_csv_file("bittrex.csv", Trade.get_fields(), bittrex_order)
    """

    key = get_key_by_exchange(EXCHANGE.BINANCE)

    last_order_id = None # 19110542000
    limit =200

    binance_order = []
    for pair_name in BINANCE_CURRENCY_PAIRS:
        # error_code, json_document = get_order_history_for_time_interval_binance(key, pair_name, limit, last_order_id)
        error_code, json_document = get_trades_history_binance(key, pair_name, limit, last_order_id)

        for entry in json_document:
            binance_order.append(Trade.from_binance_history(entry, pair_name))

    save_to_csv_file("binance.csv", Trade.get_fields(), binance_order)