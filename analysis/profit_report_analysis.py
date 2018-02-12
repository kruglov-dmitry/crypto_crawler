from collections import defaultdict, Counter

from enums.deal_type import DEAL_TYPE
from utils.exchange_utils import get_fee_by_exchange
from utils.currency_utils import get_pair_name_by_id
from utils.file_utils import log_to_file
from utils.string_utils import float_to_str
from utils.time_utils import ts_to_string


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


def save_report(start_time, end_time, overall_profit, profit_by_pairs, profit_by_pair_bitcoins,
                missing_orders, failed_orders, loss_by_pair, loss_by_pair_bitcoin, file_name="what_we_have_at_the_end.log"):
    msg = "Profit report for time period of {t1} - {t2}".format(t1=ts_to_string(start_time), t2=ts_to_string(end_time))
    log_to_file(msg, file_name)

    log_to_file("Total profit - {p}".format(p=overall_profit), file_name)

    log_to_file("\t\tProfit by pairs", file_name)

    for pair_id in profit_by_pairs:
        pair_name = get_pair_name_by_id(pair_id)
        log_to_file("PairName: {pn}     Volume: {p}     BTC: {btc}".format(pn=pair_name,
                                                                           p=float_to_str(profit_by_pairs[pair_id]),
                                                                           btc=float_to_str(profit_by_pair_bitcoins[pair_id])),
                    file_name)

    msg = "Number of timeouted(?) or failed orders. [No order_id present]   {n}".format(n=len(missing_orders))
    log_to_file(msg, file_name)

    for x in missing_orders:
        log_to_file(x, "missing_orders.log")

    for x in failed_orders:
        log_to_file(x, "NULL_deal_id.log")

    log_to_file("\t\tLOSS DETAILS", file_name)

    for pair_id in loss_by_pair_bitcoin:
        pair_name = get_pair_name_by_id(pair_id)
        log_to_file("PairName: {pn}     Volume: {p}     BTC: {btc}".format(pn=pair_name,
                                                                           p=float_to_str(loss_by_pair[pair_id]),
                                                                           btc=float_to_str(loss_by_pair_bitcoin[pair_id])),
                    file_name)
