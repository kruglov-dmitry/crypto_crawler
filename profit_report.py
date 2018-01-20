from data.Trade import Trade

from dao.db import init_pg_connection
from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE

from utils.key_utils import load_keys

from utils.exchange_utils import get_fee_by_exchange
from utils.currency_utils import get_pair_name_by_id

from collections import defaultdict, Counter

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc
from utils.string_utils import float_to_str
from dao.db import get_all_orders


def group_by_pair_and_arbitrage_id(order_list):
    res = defaultdict(list)

    tmp = defaultdict(list)
    for entry in order_list:
        tmp[str(entry.volume)].append(entry)

    for arbitrage_id in tmp:
        if len(tmp[arbitrage_id]) != 2:
            log_to_file("NOT FOUND deals for volume {a_id}".format(a_id=arbitrage_id),
                        "what_we_have_at_the_end.log")
        else:
            deal_1, deal_2 = tmp[arbitrage_id]
            if deal_1.trade_type == DEAL_TYPE.SELL:
                res[deal_1.pair_id].append((deal_1, deal_2))
            else:
                res[deal_1.pair_id].append((deal_2, deal_1))

    return res


def find_corresponding_trades(deal_from_bot, trade_history):
    res = []
    tot_volume = 0.0
    if deal_from_bot.exchange_id in [EXCHANGE.BITTREX, EXCHANGE.POLONIEX]:
        if deal_from_bot.pair_id in trade_history:
            res = [x for x in trade_history[deal_from_bot.pair_id] if x.deal_id == deal_from_bot.deal_id]
        else:
            log_to_file("NOT FOUND deal in history for {a_id}".format(a_id=deal_from_bot),
                        "what_we_have_at_the_end.log")
    elif deal_from_bot.exchange_id == EXCHANGE.BINANCE:
        if deal_from_bot.pair_id in trade_history:
            for trade in trade_history[deal_from_bot.pair_id]:
                if trade.trade_type == deal_from_bot.trade_type and 0 < deal_from_bot.execute_time - trade.execute_time < 2 \
                        and deal_from_bot.volume >= tot_volume:
                    tot_volume += trade.volume
                    res.append(trade)

        if len(res) == 0:
            log_to_file("NOT FOUND deal in history for {a_id}".format(a_id=deal_from_bot),
                        "what_we_have_at_the_end.log")
    else:
        raise

    return res


def compute_profit_by_arbitrage(buy_deal, deal_1_trades, sell_deal, deal_2_trades):
    """

                NOTE: pair of deal_1 & deal_2 should be already in proper direction

    :param buy_deal:
    :param sell_deal:
    :param trades_exchange_1:
    :param trades_exchange_2:
    :return:
    """

    # This is how we approximate profit for TG messaging
    expected_profit = buy_deal.volume * buy_deal.price * 0.01 * (100 - get_fee_by_exchange(buy_deal.exchange_id)) - \
                      sell_deal.volume * sell_deal.price * 0.01 * (100 + get_fee_by_exchange(sell_deal.exchange_id))

    """deal_1_trades = find_corresponding_trades(deal_1, trades_exchange_1)
    deal_2_trades = find_corresponding_trades(deal_2, trades_exchange_2)"""

    actual_profit = 0.0
    # tot_volume = 0.0
    for b in deal_1_trades:
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
    for b in deal_2_trades:
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


def group_by_pair_and_exchange_id(history_orders):
    poloniex_orders_by_pair = defaultdict(list)
    bittrex_orders_by_pair = defaultdict(list)
    binance_orders_by_pair = defaultdict(list)

    for entry in history_orders:
        if entry.exchange_id == EXCHANGE.POLONIEX:
            poloniex_orders_by_pair[entry.pair_id].append(entry)
        elif entry.exchange_id == EXCHANGE.BITTREX:
            bittrex_orders_by_pair[entry.pair_id].append(entry)
        elif entry.exchange_id == EXCHANGE.BINANCE:
            binance_orders_by_pair[entry.pair_id].append(entry)

    return binance_orders_by_pair, bittrex_orders_by_pair, poloniex_orders_by_pair


def group_by_pair_id(binance_trades):
    res = defaultdict(list)
    for entry in binance_trades:
        res[entry.pair_id].append(entry)
    return res


def group_binance_trades_per_order(binance_orders_at_exchange, binance_trades_group_by_pair):
    orders_with_trades = []

    last_trade_idx = Counter()
    for order in binance_orders_at_exchange:
        if order.executed_volume == 0.0:
            continue

        # DBG
        # if order.pair_id != 41:
        #    continue

        # msg = """STARTED for order - {wtf}
        #   LAST_ID is {lid}
        #    """.format(wtf=order, lid=last_trade_idx[order.pair_id])
        #log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")


        list_to_check = binance_trades_group_by_pair[order.pair_id][last_trade_idx[order.pair_id]:]

        if len(list_to_check) == 0:
            msg = """LENGTH IS ZERO
                current order: {o}
                current last_id - {lid}
                PREV list:""".format(o=order, lid=last_trade_idx[order.pair_id])
            log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")
            for twt in binance_trades_group_by_pair[order.pair_id]:
                log_to_file(twt, get_pair_name_by_id(order.pair_id) + ".txt")

            raise

        total_volume = float(0.0)
        cur_trade_list = []

        for trade in list_to_check:
            if abs(order.executed_volume - total_volume) > 0.00000001:

                total_volume += trade.volume
                cur_trade_list.append(trade)
                last_trade_idx[order.pair_id] += 1

                # msg = """ADD NEW TRADE - {o}
                #    LAST_ID NOW IS {lid}
                #    total_volume = {tv}
                #    order.executed_volume = {ev}
                #    WTF = {wtf}
                #    DIFF: {wtf1}
                #    """.format(o=trade, lid=last_trade_idx[order.pair_id], tv=total_volume, ev=order.executed_volume,
                #               wtf=order.executed_volume > total_volume, wtf1=order.executed_volume - total_volume)
                #log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")

                if total_volume - order.executed_volume > 0.000001:
                    msg = """current order: {o}
                                    current last_id - {lid}
                                    PREV list:""".format(o=order, lid=last_trade_idx[order.pair_id])
                    log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")
                    for twt in binance_trades_group_by_pair[order.pair_id]:
                        log_to_file(twt, get_pair_name_by_id(order.pair_id) + ".txt")
                    print "YOUR PROBLEM IS ", order.pair_id, get_pair_name_by_id(order.pair_id)
                    raise
            else:
                # log_to_file("SHOULD BE ENOUGH VOLUME", get_pair_name_by_id(order.pair_id) + ".txt")
                break

        # msg = """Added succesfully: {o}
        #    Tweak id - {lid}
        #    Deals size: {ds}
        #    CORRESPONDING TRADES:
        #    """.format(o=order, lid=last_trade_idx[order.pair_id], ds=len(cur_trade_list))
        #log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")
        #for x in cur_trade_list:
        #    log_to_file(x, get_pair_name_by_id(order.pair_id) + ".txt")

        orders_with_trades.append((order, cur_trade_list))

    cnt = 0
    for order, trade_list in orders_with_trades:
        log_to_file("For order - {o} CORRESPONDING trades are".format(o=order), "fucking_binance.txt")
        wut = next((x for x in binance_orders_at_bot if x.deal_id == order.deal_id), None)

        if len(trade_list) == 0 and wut is not None:
            msg = """NOT FOUND TRADES FOR: {o} 
                within bot it was registered as: {oo}""".format(o=order, oo=wut)

            log_to_file(msg, "missing_binance_orders.txt")

        # for trade in trade_list:
        #    log_to_file(trade, "fucking_binance.txt")

    # raise

    return orders_with_trades


def compute_time_key(timest, rounding_interval):
    return rounding_interval * long(timest / rounding_interval)

def compute_profit_by_pair(trades_to_order_by_pair):
    profit_by_pair = 0.0

    orders_by_volume = defaultdict(list)

    # 1 stage group by arbitrage id
    for order, trades in trades_to_order_by_pair:
        orders_by_volume[order.volume].append( (order, trades) )

    cnt = 0
    for arbitrage_id in orders_by_volume:
        if len(orders_by_volume[arbitrage_id]) == 1:
            for order, ll in orders_by_volume[arbitrage_id]:
                msg = "can't find pair order - {o}".format(o=order)
                log_to_file(msg, "missing_" + get_pair_name_by_id(order.pair_id) + ".txt")
                cnt += 1
        elif len(orders_by_volume[arbitrage_id]) > 2:

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

            list_of_orders = [x for x,y in orders_by_volume[arbitrage_id]]

            trades_by_order_id = defaultdict(list)
            for x, y in orders_by_volume[arbitrage_id]:
                trades_by_order_id[x.deal_id].append( (x,y) )

            for x in trades_by_order_id[arbitrage_id]:
                if len(trades_by_order_id[x])!=1:
                    raise

            for order1, trade_list in orders_by_volume[arbitrage_id]:
                order_pair = find_candidates(order1, list_of_orders)
                if order_pair is not None:
                    xxxxxxx, order_pair_trades = trades_by_order_id[order_pair.deal_id][0]

                    if order1.deal_id not in deal_ids and order_pair.deal_id not in deal_ids:
                        deal_ids[order1.deal_id].append( (order1, trade_list) )
                        deal_ids[order1.deal_id].append( (order_pair, order_pair_trades) )
                else:
                    msg = "can't find pair order - {o}".format(o=order1)
                    log_to_file(msg, "missing_" + get_pair_name_by_id(order1.pair_id) + ".txt")
                    cnt += 1

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
            deal_1, deal_1_trades = orders_by_volume[arbitrage_id][0]
            deal_2, deal_2_trades = orders_by_volume[arbitrage_id][1]

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

    print cnt

    return profit_by_pair

if __name__ == "__main__":
    pg_conn = init_pg_connection(_db_host="192.168.1.106", _db_port=5432)
    load_keys("./secret_keys")

    # pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com",
    #                             _db_port=5432, _db_name="crypto")

    now_time = get_now_seconds_utc()
    fews_days_ago = now_time - 5 * 24 * 60 * 60

    orders = get_all_orders(pg_conn, table_name="orders")
    binance_orders_at_bot = [x for x in orders if x.exchange_id == EXCHANGE.BINANCE]
    binance_orders_at_exchange = get_all_orders(pg_conn, table_name="binance_order_history")
    history_trades = get_all_orders(pg_conn, table_name="trades_history")

    binance_orders_at_exchange = [x for x in binance_orders_at_exchange if x.create_time >= fews_days_ago]
    history_trades = [x for x in history_trades if x.create_time >= fews_days_ago]

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
                    list_of_missing_orders.append(order)

    # 2 stage - filling order->trades list for Binances
    binance_trades = [x for x in history_trades if x.exchange_id == EXCHANGE.BINANCE]

    binance_trades.sort(key=lambda x: x.create_time, reverse=False)
    binance_trades_group_by_pair = group_by_pair_id(binance_trades)
    binance_orders_at_exchange.sort(key=lambda x: x.create_time, reverse=False)

    binance_orders_at_exchange = [x for x in binance_orders_at_exchange if x.create_time >= fews_days_ago]

    orders_with_trades = group_binance_trades_per_order(binance_orders_at_exchange, binance_trades_group_by_pair)

    orders_with_corresponding_trades += orders_with_trades

    # 3 stage - bucketing all that crap by pair_id
    trades_to_order = defaultdict(list)
    for order, trade_list in orders_with_corresponding_trades:
        trades_to_order[order.pair_id].append( (order, trade_list))

    profit_by_pairs = Counter()

    for pair_id in trades_to_order:
        profit_by_pairs[pair_id] = compute_profit_by_pair(trades_to_order[pair_id])

    overall_profit = sum(profit_by_pairs.itervalues())

    log_to_file("Total profit - {p}".format(p=overall_profit), "what_we_have_at_the_end.log")
    log_to_file("Profit by pairs", "what_we_have_at_the_end.log")
    for pair_id in profit_by_pairs:
        pair_name = get_pair_name_by_id(pair_id)
        log_to_file("{pn} - {p}".format(pn=pair_name, p=float_to_str(profit_by_pairs[pair_id])),
                    "what_we_have_at_the_end.log")


    for x in list_of_missing_orders:
        log_to_file(x, "missing_orders.log")

    for x in failed_deal_ids:
        log_to_file(x, "NULL_deal_id.log")











def some_ther_code():
    # time bucketing option
    trade_by_timest = defaultdict(list)
    order_by_timest = defaultdict(list)


    for every_trade in binance_trades:
        trade_by_timest[every_trade.execute_time].append(every_trade)

    for every_order in binance_orders_at_exchange:
        order_by_timest[every_order.execute_time].append(every_order)

    orders_with_trades = []
    for ts in order_by_timest:
        last_idx = 0
        for order in order_by_timest[ts]:
            total_volume = 0.0
            cur_trade_list = []
            cur_idx = 0
            for trade in trade_by_timest[ts][last_idx:]:
                cur_idx += 1
                if order.volume > total_volume:
                    total_volume += trade.volume
                    cur_trade_list.append(trade)
                else:
                    last_idx = cur_idx
                    break

            orders_with_trades.append( (order, cur_trade_list) )




    orders_by_pair = group_by_pair_and_arbitrage_id(orders)



    binance_orders_by_pair, bittrex_orders_by_pair, poloniex_orders_by_pair = group_by_pair_and_exchange_id(history_trades)

    overall_profit = 0.0
    profit_by_pairs = {}


    def get_corresponding_trades(exchange_id):
        return {
            EXCHANGE.BINANCE: binance_orders_by_pair,
            EXCHANGE.POLONIEX: poloniex_orders_by_pair,
            EXCHANGE.BITTREX: bittrex_orders_by_pair
        }[exchange_id]

    # FIXME NOTE: Open question how to choose proper direction of arbitrage?

    for pair_id in orders_by_pair:
        profit_by_pairs[pair_id] = 0.0
        for sell_deal, buy_deal in orders_by_pair[pair_id]:
            trade_history1 = get_corresponding_trades(sell_deal.exchange_id)
            trades_1 = find_corresponding_trades(sell_deal, trade_history1)
            if len(trades_1) == 0:
                log_to_file("NOT FOUND! {tr}".format(tr=sell_deal),
                            "what_we_have_at_the_end.log")

            trade_history2 = get_corresponding_trades(buy_deal.exchange_id)
            trades_2 = find_corresponding_trades(buy_deal, trade_history2)
            if len(trades_2) == 0:
                log_to_file("NOT FOUND! {tr}".format(tr=buy_deal),
                            "what_we_have_at_the_end.log")

            if buy_deal.volume == 912.0 and buy_deal.pair_id == 25.0:
                print "SELL DEAL from BOT", sell_deal
                print "TOTAL: ",  len(trades_1), "Corresponding trades from history"
                for b in trades_1:
                    print b

                print "BUY DEAL from BOT", buy_deal
                print "TOTAL: ",  len(trades_2), "Corresponding trades from history"
                for b in trades_2:
                    print b

                # raise

            if len(trades_1) > 0 and len(trades_2) > 0:
                profit_by_pairs[pair_id] += compute_profit_by_arbitrage(sell_deal, trades_1, buy_deal, trades_2)
