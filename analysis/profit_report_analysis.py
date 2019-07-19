from collections import defaultdict, Counter

from analysis.classes.LossDetails import LossDetails

from enums.deal_type import DEAL_TYPE
from utils.exchange_utils import get_fee_by_exchange, get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id, get_currency_name_by_id, split_currency_pairs
from utils.file_utils import log_to_file
from utils.string_utils import float_to_str
from utils.time_utils import ts_to_string_local

# OLAP :(
from analysis.grouping_utils import group_orders_by_arbitrage_id


def compute_profit_by_pair(pair_id, trades_to_order_by_pair):

    file_name = get_pair_name_by_id(pair_id) + "_trace.txt"

    profit_coin = 0.0
    profit_base_currency = 0.0

    orders_by_arbitrage_id = defaultdict(list)
    # 1 stage group by arbitrage id
    for order, trades in trades_to_order_by_pair:
        orders_by_arbitrage_id[order.arbitrage_id].append((order, trades))

    number_of_missing_pair = 0
    for arbitrage_id in orders_by_arbitrage_id:
        if len(orders_by_arbitrage_id[arbitrage_id]) == 1:
            number_of_missing_pair += 1
            msg = "Can't find paired arbitrage order for {arbitrage_id} {o}".format(
                arbitrage_id=arbitrage_id, o=orders_by_arbitrage_id[arbitrage_id][0])
            log_to_file(msg, file_name)
            continue
        else:
            for order, trades in orders_by_arbitrage_id[arbitrage_id]:
                msg = "Computing trades for order {o}".format(o=order)
                log_to_file(msg, file_name)
                if order.trade_type == DEAL_TYPE.BUY:
                    for trade in trades:
                        profit_coin += trade.executed_volume
                        base_currency_volume = trade.executed_volume * trade.price * 0.01 * (100 + get_fee_by_exchange(trade.exchange_id))
                        profit_base_currency -= base_currency_volume
                        msg = """Analysing trade {o}
                        ADD coin volume = {cv}
                        SUBTRACT base currency = {base}
                        """.format(o=trade, cv=trade.executed_volume, base=base_currency_volume)
                        log_to_file(msg, file_name)
                elif order.trade_type == DEAL_TYPE.SELL:
                    for trade in trades:
                        profit_coin -= trade.executed_volume
                        base_currency_volume = trade.executed_volume * trade.price * 0.01 * (100 - get_fee_by_exchange(trade.exchange_id))
                        profit_base_currency += base_currency_volume
                        msg = """Analysing trade {o}
                        SUBTRACT coin volume = {cv}
                        ADD base currency = {base}
                        """.format(o=trade, cv=trade.executed_volume, base=base_currency_volume)
                        log_to_file(msg, file_name)
                else:
                    print "WE HAVE WRONG trade_type", order.trade_type
                    print "For order: ", order

    msg = "For {pair_name} Number of missing paired order is {num}".format(pair_name=get_pair_name_by_id(pair_id), num=number_of_missing_pair)
    log_to_file(msg, file_name)

    return profit_coin, profit_base_currency


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

    loss_details = defaultdict(list)
    loss_details_total = Counter()

    for pair_id in orders_by_pair:
        loss_by_coin, loss_by_base_coin = compute_loss_by_pair(orders_by_pair[pair_id])
        base_currency_id, dst_currency_id = split_currency_pairs(pair_id)
        loss_details[base_currency_id].append(LossDetails(base_currency_id, dst_currency_id, pair_id, loss_by_coin, loss_by_base_coin))

        loss_details_total[base_currency_id] += loss_by_base_coin

    return loss_details, loss_details_total


def compute_loss_by_pair(orders_and_trades_by_pair):
    volume_pair = 0.0
    volume_base_currency = 0.0

    for order, trade_list in orders_and_trades_by_pair:
        if order.trade_type == DEAL_TYPE.BUY:
            for trade in trade_list:
                volume_pair += trade.executed_volume
                volume_base_currency -= trade.executed_volume * trade.price * 0.01 * (100 - get_fee_by_exchange(trade.exchange_id))
        elif order.trade_type == DEAL_TYPE.SELL:
            for trade in trade_list:
                volume_pair -= trade.executed_volume
                volume_base_currency += trade.executed_volume * trade.price * 0.01 * (100 - get_fee_by_exchange(trade.exchange_id))

    return volume_pair, volume_base_currency


def save_report(start_time, end_time, profit_by_base, profit_details,
                missing_orders, failed_orders, loss_details, loss_by_base,
                orders, history_trades,
                file_name="what_we_have_at_the_end.log"):
    msg = "Profit report for time period of {t1} - {t2}".format(t1=ts_to_string_local(start_time), t2=ts_to_string_local(end_time))
    log_to_file(msg, file_name)
    msg = "Epoch format: {t1} - {t2}".format(t1=start_time, t2=end_time)
    log_to_file(msg, file_name)

    orders_by_arbitrage_id = group_orders_by_arbitrage_id(orders)

    log_to_file("Total number of arbitrage events - {p}".format(p=len(orders_by_arbitrage_id)), file_name)
    log_to_file("For them we registered - {p} orders".format(p=len(orders)), file_name)
    log_to_file("Resulted number of trades - {p}".format(p=len(history_trades)), file_name)

    for base_currency_id in profit_details:

        log_to_file("\t\tTotal profit by {cn} - {nn}".format(cn=get_currency_name_by_id(base_currency_id),
                                                             nn=float_to_str(profit_by_base[base_currency_id])),
                    file_name)

        for details_by_pair_id in profit_details[base_currency_id]:
            log_to_file(details_by_pair_id, file_name)

    total_number_missing = 0
    for entry in missing_orders:
        total_number_missing += len(missing_orders[entry])

    msg = "Total number of orders without trades (Expired?): {n}".format(n=total_number_missing)
    log_to_file(msg, file_name)
    for exchange_id in missing_orders:
        msg = "\t{exch}     Number of orders without trades: {n}".format(exch=get_exchange_name_by_id(exchange_id),
                                                                         n=len(missing_orders[exchange_id]))
        log_to_file(msg, file_name)

    for exchange_id in missing_orders:
        msg = "Missing orders for {exch}".format(exch=get_exchange_name_by_id(exchange_id))
        log_to_file(msg, "missing_orders.log")
        for x in missing_orders[exchange_id]:
            log_to_file(x, "missing_orders.log")

    total_number_failed = 0
    for exchange_id in failed_orders:
        total_number_failed += len(failed_orders[exchange_id])

    msg = "Total number of orders without order_id (Failed?): {n}".format(n=total_number_failed)
    log_to_file(msg, file_name)
    for exchange_id in failed_orders:
        msg = "\t{exch}     Number of orders without trades: {n}".format(exch=get_exchange_name_by_id(exchange_id),
                                                                         n=len(failed_orders[exchange_id]))
        log_to_file(msg, file_name)

    for exchange_id in failed_orders:
        msg = "Failed orders for {exch}".format(exch=get_exchange_name_by_id(exchange_id))
        log_to_file(msg, "failed_orders.log")
        for x in failed_orders[exchange_id]:
            log_to_file(x, "failed_orders.log")

    log_to_file("\t\tLOSS DETAILS", file_name)

    for base_currency_id in loss_details:
        log_to_file("\t\tLoss details by {cn} - {nn}".format(cn=get_currency_name_by_id(base_currency_id),
                                                             nn=float_to_str(loss_by_base[base_currency_id])),
                    file_name)

        for details_by_pair_id in loss_details[base_currency_id]:
            log_to_file(details_by_pair_id, file_name)
