import csv

from data.Trade import Trade

from dao.db import init_pg_connection, get_all_orders
from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE

from utils.key_utils import load_keys, get_key_by_exchange
from utils.time_utils import get_now_seconds_utc

from poloniex.market_utils import get_order_history_for_time_interval_poloniex
from poloniex.currency_utils import get_currency_pair_from_poloniex
from bittrex.market_utils import get_order_history_for_time_interval_bittrex
from bittrex.currency_utils import get_currency_pair_from_bittrex
from binance.market_utils import get_order_history_for_time_interval_binance, get_trades_history_binance
from binance.currency_utils import get_currency_pair_from_binance
from binance.constants import BINANCE_CURRENCY_PAIRS

from utils.exchange_utils import get_fee_by_exchange

from collections import defaultdict

from utils.file_utils import log_to_file
from utils.currency_utils import get_pair_name_by_id
from utils.string_utils import float_to_str


def save_to_csv_file(file_name, fields_list, array_list):

    with open(file_name, 'w') as f:
        writer = csv.writer(f, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fields_list)
        for cdr in array_list:
            writer.writerow(list(cdr))


def group_by_pair_and_arbitrage_id(order_list):
    res = defaultdict(list)

    tmp = defaultdict(list)
    for entry in order_list:
        tmp[entry.arbitrage_id].append(entry)

    for arbitrage_id in tmp:
        deal_1, deal_2 = tmp[arbitrage_id]
        if deal_1.trade_type == DEAL_TYPE.BUY:
            res[deal_1.pair_id].append((deal_1, deal_2))
        else:
            res[deal_1.pair_id].append((deal_2, deal_1))

    return res


def find_corresponding_trades(deal, trade_history):
    res = []

    if deal.exchange_id in [EXCHANGE.BITTREX, EXCHANGE.POLONIEX]:
        res = [x for x in trade_history if x.deal_id == deal.deal_id if x.pair_id == deal.pair_id]
    elif deal.exchange_id == EXCHANGE.BINANCE:
        for trade in trade_history:
            if trade.pair_id == deal.pair_id and trade.exchange_id == deal.exchange_id and \
                                    trade.execute_time - deal.create_time <= 20:
                res.append(trade)
    else:
        raise

    return res


def compute_profit_by_arbitrage(deal_1, trades_exchange_1, deal_2, trades_exchange_2):
    """

                NOTE: pair of deal_1 & deal_2 should be already in proper direction

    :param deal_1:
    :param deal_2:
    :param trades_exchange_1:
    :param trades_exchange_2:
    :return:
    """

    # This is how we approximate profit for TG messaging
    expected_profit = deal_1.volume * deal_1.price * 0.01 * (100 - get_fee_by_exchange(deal_1.exchange_id)) - \
               deal_2.volume * deal_2.price * 0.01 * (100 + get_fee_by_exchange(deal_2.exchange_id))

    deal_1_trades = find_corresponding_trades(deal_1, trades_exchange_1)
    deal_2_trades = find_corresponding_trades(deal_2, trades_exchange_2)

    actual_profit = 0.0
    for b in deal_1_trades:
        actual_profit += b.volume * b.price * 0.01 * (100 - get_fee_by_exchange(b.exchange_id))

    for b in deal_2_trades:
        actual_profit = actual_profit - b.volume * b.price * 0.01 * (100 + get_fee_by_exchange(b.exchange_id))

    # FIXME NOTE: check ratio expected - actual

    return actual_profit


if __name__ == "__main__":
    load_keys("./secret_keys")

    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
                                 _db_port=5432, _db_name="crypto")

    orders = get_all_orders(pg_conn)

    # save_to_csv_file("tst.csv", Trade.get_fields(), orders)
    now_time = get_now_seconds_utc()
    two_days_ago = now_time - 2 * 24 * 60 * 60

    key = get_key_by_exchange(EXCHANGE.POLONIEX)
    error_code, json_document = get_order_history_for_time_interval_poloniex(key, pair_name='all',
                                                                             time_start=two_days_ago,
                                                                             time_end=now_time, limit=10000)

    orders_by_pair = group_by_pair_and_arbitrage_id(orders)

    poloniex_orders_by_pair = defaultdict(list)
    for pair_name in json_document:
        for entry in json_document[pair_name]:
            pair_id = get_currency_pair_from_poloniex(pair_name)
            poloniex_orders_by_pair[pair_id].append(Trade.from_poloniex_history(entry, pair_name))

    # save_to_csv_file("poloniex.csv", Trade.get_fields(), res)

    key = get_key_by_exchange(EXCHANGE.BITTREX)
    error_code, json_document = get_order_history_for_time_interval_bittrex(key, pair_name='all')

    bittrex_order_by_pair = defaultdict(list)
    for entry in json_document["result"]:
        new_trade = Trade.from_bittrex_history(entry)
        bittrex_order_by_pair[new_trade.pair_id].append(new_trade)

    """
    save_to_csv_file("bittrex.csv", Trade.get_fields(), bittrex_order)
    """

    key = get_key_by_exchange(EXCHANGE.BINANCE)

    last_order_id = None # 19110542000
    limit = 200

    binance_order = []
    for pair_name in BINANCE_CURRENCY_PAIRS:
        # error_code, json_document = get_order_history_for_time_interval_binance(key, pair_name, limit, last_order_id)
        error_code, json_document = get_trades_history_binance(key, pair_name, limit, last_order_id)

        for entry in json_document:
            pair_id = get_currency_pair_from_binance(pair_name)
            binance_order.append(Trade.from_binance_history(entry, pair_name))

    """
    save_to_csv_file("binance.csv", Trade.get_fields(), binance_order)
    """

    overall_profit = 0.0
    profit_by_pairs = {}


    def get_corresponding_trades(exchange_id):
        return {
            EXCHANGE.BINANCE: binance_order,
            EXCHANGE.POLONIEX: poloniex_orders_by_pair,
            EXCHANGE.BITTREX: bittrex_order_by_pair
        }[exchange_id]

    # FIXME NOTE: Open question how to choose proper direction of arbitrage?

    for pair_id in orders_by_pair:
        profit_by_pairs[pair_id] = 0.0
        for buy_deal, sell_deal in orders_by_pair[pair_id]:
            trade_history1 = get_corresponding_trades(buy_deal.exchange_id)
            trades_1 = find_corresponding_trades(buy_deal, trade_history1)
            if len(trades_1) == 0:
                log_to_file("NOT FOUND! {tr}".format(tr=buy_deal),
                            "what_we_have_at_the_end.log")

            trade_history2 = get_corresponding_trades(sell_deal.exchange_id)
            trades_2 = find_corresponding_trades(buy_deal, trade_history2)
            if len(trades_2) == 0:
                log_to_file("NOT FOUND! {tr}".format(tr=sell_deal),
                            "what_we_have_at_the_end.log")

            if len(trades_1) > 0 and len(trades_2) > 0:
                profit_by_pairs[pair_id] += compute_profit_by_arbitrage(buy_deal, trade_history1, sell_deal, trade_history2)


    overall_profit = sum(profit_by_pairs.itervalues())

    log_to_file("Total profit - {p}".format(p=overall_profit), "what_we_have_at_the_end.log")
    log_to_file("Profit by pairs", "what_we_have_at_the_end.log")
    for pair_id in profit_by_pairs:
        pair_name = get_pair_name_by_id(pair_id)
        log_to_file("{pn} - {p}".format(pn=pair_name, p=float_to_str(profit_by_pairs[pair_id])),
                    "what_we_have_at_the_end.log")

