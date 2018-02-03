from collections import defaultdict, Counter
import sys
import ConfigParser

from dao.db import get_all_orders, init_pg_connection

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE

from utils.currency_utils import get_pair_name_by_id
from utils.exchange_utils import get_fee_by_exchange
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from utils.string_utils import float_to_str
from utils.time_utils import get_now_seconds_utc, ts_to_string

from analysis.data_load_for_profit_report import fetch_trades_history_to_db
from analysis.binance_order_by_trades import group_binance_trades_per_order


def compute_profit_by_arbitrage(buy_order, buy_trades, sell_order, sell_trades):
    """

                NOTE: pair of deal_1 & deal_2 should be already in proper direction

    :param buy_order:
    :param sell_order:
    :param trades_exchange_1:
    :param trades_exchange_2:
    :return:
    """

    # This is how we approximate profit for TG messaging
    expected_profit = buy_order.volume * buy_order.price * 0.01 * (100 - get_fee_by_exchange(buy_order.exchange_id)) - \
                      sell_order.volume * sell_order.price * 0.01 * (100 + get_fee_by_exchange(sell_order.exchange_id))

    actual_profit = 0.0
    # tot_volume = 0.0
    for b in buy_trades:
        actual_profit += b.volume * b.price * 0.01 * (100 - get_fee_by_exchange(b.exchange_id))
        """ tot_volume += b.volume
        if tot_volume > deal_1.volume:
            print deal_1
            print tot_volume, deal_1.volume
            for zz in deal_1_trades:
                print zz
            raise
        """

    # tot_volume = 0.0
    for b in sell_trades:
        actual_profit = actual_profit - b.volume * b.price * 0.01 * (100 + get_fee_by_exchange(b.exchange_id))
        """tot_volume += b.volume
        if tot_volume > deal_2.volume:
            print deal_2
            print tot_volume, deal_2.volume
            for zz in deal_2_trades:
                print zz
            raise"""

    # FIXME NOTE: check ratio expected - actual

    return actual_profit


def group_by_pair_id(binance_trades):
    res = defaultdict(list)
    for entry in binance_trades:
        res[entry.pair_id].append(entry)
    return res


def compute_profit_by_pair(pair_id, trades_to_order_by_pair):

    file_name = get_pair_name_by_id(pair_id) + "_trace.txt"

    profit_coin = 0.0
    profit_bitcoin = 0.0

    orders_by_arbitrage_id = defaultdict(list)
    # 1 stage group by arbitrage id
    for order, trades in trades_to_order_by_pair:
        orders_by_arbitrage_id[order.arbitrage_id].append((order, trades))

    number_of_missing_pair = 0
    for arbitrage_id in orders_by_arbitrage_id:
        if len(orders_by_arbitrage_id[arbitrage_id]) == 1:
            number_of_missing_pair += 1
            msg = "Can't find paired arbitrage order for {o}".format(o=orders_by_arbitrage_id[arbitrage_id][0])
            log_to_file(msg, file_name)
            continue
        else:
            for order, trades in orders_by_arbitrage_id[arbitrage_id]:
                msg = "Computing trades for order {o}".format(o=order)
                log_to_file(msg, file_name)
                if order.trade_type == DEAL_TYPE.BUY:
                    for trade in trades:
                        profit_coin += trade.executed_volume
                        bitcoin_volume = trade.executed_volume * trade.price * 0.01 * (100 + get_fee_by_exchange(trade.exchange_id))
                        profit_bitcoin -= bitcoin_volume
                        msg = """Analysing trade {o}
                        ADD coin volume = {cv}
                        SUBTRACT bitcoin = {btc}
                        """.format(o=trade, cv=trade.executed_volume, btc=profit_bitcoin)
                        log_to_file(msg, file_name)
                elif order.trade_type == DEAL_TYPE.SELL:
                    for trade in trades:
                        profit_coin -= trade.executed_volume
                        bitcoin_volume = trade.executed_volume * trade.price * 0.01 * (100 - get_fee_by_exchange(trade.exchange_id))
                        profit_bitcoin += bitcoin_volume
                        msg = """Analysing trade {o}
                        SUBTRACT coin volume = {cv}
                        ADD bitcoin = {btc}
                        """.format(o=trade, cv=trade.executed_volume, btc=bitcoin_volume)
                        log_to_file(msg, file_name)

    msg = "For {pair_name} Number of missing paired order is {num}".format(pair_name=get_pair_name_by_id(pair_id), num=number_of_missing_pair)
    log_to_file(msg, file_name)

    return profit_coin, profit_bitcoin


def compute_profit_by_pair_using_volume(trades_to_order_by_pair):
    profit_by_pair = 0.0

    orders_by_arbitrage_id = defaultdict(list)
    # 1 stage group by arbitrage id
    for order, trades in trades_to_order_by_pair:
        orders_by_arbitrage_id[order.arbitrage_id].append((order, trades))

    number_of_missing_pair = 0
    for arbitrage_id in orders_by_arbitrage_id:
        if len(orders_by_arbitrage_id[arbitrage_id]) == 1:
            continue
        elif len(orders_by_arbitrage_id[arbitrage_id]) > 2:
            def find_candidates(order, some_list):
                # pair_id and volume the same
                res = []
                for entry in some_list:
                    if order.deal_id != entry.deal_id and abs(order.create_time - entry.create_time) < 10:

                        res.append(entry)
                if len(res) != 1:
                    """print "What we search for: ", order
                    print "List"
                    for b in some_list:
                        print b
                    print "RESULT:"
                    for b in res:
                        print b"""
                    return None
                else:
                    return res[0]

            deal_ids = defaultdict(list)

            list_of_orders = [x for x,y in orders_by_arbitrage_id[arbitrage_id]]

            trades_by_order_id = defaultdict(list)
            for x, y in orders_by_arbitrage_id[arbitrage_id]:
                trades_by_order_id[x.deal_id].append( (x,y) )

            for x in trades_by_order_id[arbitrage_id]:
                if len(trades_by_order_id[x])!=1:
                    raise

            for order1, trade_list in orders_by_arbitrage_id[arbitrage_id]:
                order_pair = find_candidates(order1, list_of_orders)
                if order_pair is not None:
                    xxxxxxx, order_pair_trades = trades_by_order_id[order_pair.deal_id][0]

                    if order1.deal_id not in deal_ids and order_pair.deal_id not in deal_ids:
                        deal_ids[order1.deal_id].append( (order1, trade_list) )
                        deal_ids[order1.deal_id].append( (order_pair, order_pair_trades) )
                else:
                    msg = "can't find pair order - {o}".format(o=order1)
                    log_to_file(msg, "missing_" + get_pair_name_by_id(order1.pair_id) + ".txt")
                    number_of_missing_pair += 1

            for grouping_id in deal_ids:
                if len(deal_ids[grouping_id])!=2:
                    print "FUCK"
                    for xxxx in deal_ids[grouping_id]:
                        print xxxx
                    raise
                else:
                    deal_1, deal_1_trades = deal_ids[grouping_id][0]
                    deal_2, deal_2_trades = deal_ids[grouping_id][1]

                    if deal_1.trade_type == DEAL_TYPE.SELL:
                        current_profit = compute_profit_by_arbitrage(deal_1, deal_1_trades, deal_2, deal_2_trades)
                        profit_by_pair += current_profit
                        msg = """DEAL1: {d1}
                                    DEAL2: {d2}
                                    calculated_profit - {cp}
                                    """.format(d1=deal_1, d2=deal_2, cp=current_profit)
                        log_to_file(msg, "arbitrage_log_" + get_pair_name_by_id(deal_1.pair_id) + ".txt")
                    else:
                        current_profit = compute_profit_by_arbitrage(deal_2, deal_2_trades, deal_1, deal_1_trades)
                        profit_by_pair += current_profit
                        msg = """DEAL1: {d1}
                                                    DEAL2: {d2}
                                                    calculated_profit - {cp}
                                                    """.format(d1=deal_2, d2=deal_1, cp=current_profit)
                        log_to_file(msg, "arbitrage_log_" + get_pair_name_by_id(deal_1.pair_id) + ".txt")
        else:
            deal_1, deal_1_trades = orders_by_arbitrage_id[arbitrage_id][0]
            deal_2, deal_2_trades = orders_by_arbitrage_id[arbitrage_id][1]

            if deal_1.trade_type == DEAL_TYPE.SELL:
                current_profit = compute_profit_by_arbitrage(deal_1, deal_1_trades, deal_2, deal_2_trades)
                profit_by_pair += current_profit
                msg = """DEAL1: {d1}
                DEAL2: {d2}
                calculated_profit - {cp}
                """.format(d1=deal_1, d2=deal_2, cp=current_profit)
                log_to_file(msg, "arbitrage_log_" + get_pair_name_by_id(deal_1.pair_id) + ".txt")
            else:
                current_profit = compute_profit_by_arbitrage(deal_2, deal_2_trades, deal_1, deal_1_trades)
                profit_by_pair += current_profit
                msg = """DEAL1: {d1}
                                DEAL2: {d2}
                                calculated_profit - {cp}
                                """.format(d1=deal_2, d2=deal_1, cp=current_profit)
                log_to_file(msg, "arbitrage_log_" + get_pair_name_by_id(deal_1.pair_id) + ".txt")

    print "Number of missing pair", number_of_missing_pair

    return profit_by_pair


def compute_loss(trades_to_order_by_pair):

    orders_by_arbitrage_id = defaultdict(list)
    # 1 stage group by arbitrage id
    for order, trades in trades_to_order_by_pair:
        orders_by_arbitrage_id[order.arbitrage_id].append((order, trades))

    orders_by_pair = defaultdict(list)

    cnt = 0
    for arbitrage_id in orders_by_arbitrage_id:
        if len(orders_by_arbitrage_id[arbitrage_id]) != 1:
            continue
        order, trades_list = orders_by_arbitrage_id[arbitrage_id][0]
        msg = "can't find pair order - {o}".format(o=order)
        log_to_file(msg, "missing_" + get_pair_name_by_id(order.pair_id) + ".txt")
        cnt += 1
        orders_by_pair[order.pair_id].append( (order, trades_list) )

    loss_by_coin = Counter()
    loss_by_coin_bitcoin = Counter()

    for pair_id in orders_by_pair:
        loss_by_coin[pair_id], loss_by_coin_bitcoin[pair_id] = compute_loss_by_pair(orders_by_pair[pair_id])

    return loss_by_coin, loss_by_coin_bitcoin


def compute_loss_by_pair(orders_and_trades_by_pair):
    volume_pair = 0.0
    volume_bitcoin = 0.0

    for order, trade_list in orders_and_trades_by_pair:
        if order.trade_type == DEAL_TYPE.BUY:
            for trade in trade_list:
                volume_pair += trade.executed_volume
                volume_bitcoin -= trade.executed_volume * trade.price * 0.01 * (100 - get_fee_by_exchange(trade.exchange_id))
        elif order.trade_type == DEAL_TYPE.SELL:
            for trade in trade_list:
                volume_pair -= trade.executed_volume
                volume_bitcoin += trade.executed_volume * trade.price * 0.01 * (100 - get_fee_by_exchange(trade.exchange_id))

    return volume_pair, volume_bitcoin


def find_order_bot_history(order_binance, order_bot_history):
    for bb in order_bot_history:
        if bb.deal_id == order_binance.deal_id:
            return bb

    return None


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

    # key_path = config.getint("common", "path_to_api_keys")
    # start_time = config.getint("common", "start_time")
    # end_time = config.getint("common", "end_time")

    end_time = get_now_seconds_utc()
    start_time = end_time - 2 * 24 * 60 * 60

    should_fetch_history_to_db = config.getboolean("common", "fetch_history_from_exchanges")

    pg_conn = init_pg_connection(_db_host=db_host, _db_port=db_port, _db_name=db_name)

    load_keys("./secret_keys")

    if should_fetch_history_to_db:
        fetch_trades_history_to_db(pg_conn, start_time)

    orders = get_all_orders(pg_conn, table_name="orders", time_start=start_time)
    binance_orders_at_bot = [x for x in orders if x.exchange_id == EXCHANGE.BINANCE]
    binance_orders_at_exchange = get_all_orders(pg_conn, table_name="binance_order_history", time_start=start_time)
    history_trades = get_all_orders(pg_conn, table_name="trades_history", time_start=start_time)

    for order_binance in binance_orders_at_exchange:
        order_bot = find_order_bot_history(order_binance, orders)
        if order_bot is not None:
            order_binance.arbitrage_id = order_bot.arbitrage_id

    """
    # FIXME modify get_all_orders_by_time
    orders = [x for x in orders if x.create_time >= start_time]
    binance_orders_at_exchange = [x for x in binance_orders_at_exchange if x.create_time >= start_time]
    history_trades = [x for x in history_trades if x.create_time >= start_time]
    """

    orders_with_corresponding_trades = []

    # 1 stage - filling order->trades list for Poloniex, Bittrex
    list_of_missing_orders = []
    failed_deal_ids = []
    for order in orders:
        if order.deal_id is None:
            failed_deal_ids.append(order)
        else:
            if order.exchange_id in [EXCHANGE.POLONIEX, EXCHANGE.BITTREX]:
                res = next((x for x in history_trades if x.deal_id == order.deal_id), None)
                if res is None:
                    list_of_missing_orders.append(order)
                else:
                    current_trades_list = []
                    for x in history_trades:
                        if x.deal_id == order.deal_id:
                            current_trades_list.append(x)
                    orders_with_corresponding_trades.append( (order, current_trades_list) )
            else:
                res = next((x for x in binance_orders_at_exchange if x.deal_id == order.deal_id), None)
                if res is None:
                    list_of_missing_orders.append(res)

    # 2 stage - filling order->trades list for Binances
    binance_trades = [x for x in history_trades if x.exchange_id == EXCHANGE.BINANCE]

    binance_trades.sort(key=lambda x: x.create_time, reverse=False)
    binance_trades_group_by_pair = group_by_pair_id(binance_trades)
    binance_orders_at_exchange.sort(key=lambda x: x.create_time, reverse=False)

    orders_with_trades = group_binance_trades_per_order(binance_orders_at_exchange, binance_trades_group_by_pair, binance_orders_at_bot)

    orders_with_corresponding_trades += orders_with_trades

    # 3 stage - bucketing all that crap by pair_id
    trades_to_order = defaultdict(list)
    for order, trade_list in orders_with_corresponding_trades:
        trades_to_order[order.pair_id].append( (order, trade_list))

    profit_by_pairs = Counter()
    profit_by_pair_bitcoins = Counter()

    for pair_id in trades_to_order:
        profit_by_pairs[pair_id], profit_by_pair_bitcoins[pair_id] = compute_profit_by_pair(pair_id, trades_to_order[pair_id])

    overall_profit = sum(profit_by_pair_bitcoins.itervalues())

    msg = "Profit report for time period of {t1} - {t2}".format(t1=ts_to_string(start_time), t2=ts_to_string(end_time))
    log_to_file(msg, "what_we_have_at_the_end.log")
    log_to_file("Total profit - {p}".format(p=overall_profit), "what_we_have_at_the_end.log")
    log_to_file("\t\tProfit by pairs", "what_we_have_at_the_end.log")
    for pair_id in profit_by_pairs:
        pair_name = get_pair_name_by_id(pair_id)
        log_to_file("PairName: {pn}     Volume: {p}     BTC: {btc}".format(pn=pair_name, p=float_to_str(profit_by_pairs[pair_id]),
                                                                       btc=float_to_str(profit_by_pair_bitcoins[pair_id])),
                    "what_we_have_at_the_end.log")

    msg = "Number of timeouted(?) or failed orders. [No order_id present]   {n}".format(n=len(list_of_missing_orders))
    log_to_file(msg, "what_we_have_at_the_end.log")

    for x in list_of_missing_orders:
        log_to_file(x, "missing_orders.log")

    for x in failed_deal_ids:
        log_to_file(x, "NULL_deal_id.log")

    log_to_file("\t\tLOSS DETAILS", "what_we_have_at_the_end.log")
    loss_by_coin, loss_by_coin_bitcoin = compute_loss(orders_with_corresponding_trades)
    for pair_id in loss_by_coin_bitcoin:
        pair_name = get_pair_name_by_id(pair_id)
        log_to_file("PairName: {pn}     Volume: {p}     BTC: {btc}".format(pn=pair_name,
                                                                           p=float_to_str(loss_by_coin[pair_id]),
                                                                           btc=float_to_str(loss_by_coin_bitcoin[pair_id])),
                    "what_we_have_at_the_end.log")
