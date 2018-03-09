from collections import defaultdict
from utils.file_utils import log_to_file

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE


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


def group_orders_by_arbitrage_id(order_list):
    res = defaultdict(list)

    for x in order_list:
        res[x.arbitrage_id].append(x)

    return res


def find_corresponding_trades(deal_from_bot, trade_history):
    res = []
    tot_volume = 0.0
    if deal_from_bot.exchange_id in [EXCHANGE.BITTREX, EXCHANGE.POLONIEX]:
        if deal_from_bot.pair_id in trade_history:
            res = [x for x in trade_history[deal_from_bot.pair_id] if x.order_id == deal_from_bot.order_id]
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
        assert False

    return res


def group_by_pair_and_exchange_id(history_orders):
    orders_by_exchange_and_pair = defaultdict(defaultdict(list))

    for entry in history_orders:
        orders_by_exchange_and_pair[entry.exchange_id][entry.pair_id].append(entry)

    return orders_by_exchange_and_pair


def group_trades_by_orders(orders, history_trades, binance_orders_at_exchange):

    # 1 stage - filling order->trades list for Poloniex, Bittrex

    missing_orders = defaultdict(list)
    failed_orders = defaultdict(list)
    orders_with_corresponding_trades = []

    for order in orders:
        if order.order_id is None:
            failed_orders[order.exchange_id].append(order)
        else:
            if order.exchange_id in [EXCHANGE.POLONIEX, EXCHANGE.BITTREX]:
                res = next((x for x in history_trades if x.order_id == order.order_id), None)
                if res is None:
                    missing_orders[order.exchange_id].append(order)
                else:
                    current_trades_list = []
                    for x in history_trades:
                        if x.order_id == order.order_id:
                            current_trades_list.append(x)
                    orders_with_corresponding_trades.append( (order, current_trades_list) )
            else:
                res = next((x for x in binance_orders_at_exchange if x.order_id == order.order_id), None)
                if res is None:
                    missing_orders[order.exchange_id].append(order)

    return missing_orders, failed_orders, orders_with_corresponding_trades


def group_by_pair_id(binance_trades):
    res = defaultdict(list)
    for entry in binance_trades:
        res[entry.pair_id].append(entry)
    return res
