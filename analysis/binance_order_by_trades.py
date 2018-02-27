from collections import Counter

from utils.file_utils import log_to_file
from utils.currency_utils import get_pair_name_by_id
from utils.string_utils import float_to_str


def group_binance_trades_per_order(binance_orders_at_exchange, binance_trades_group_by_pair, binance_orders_at_bot):
    orders_with_trades = []

    last_trade_idx = Counter()

    orders_to_check = []
    for order in binance_orders_at_bot:
        found = False
        for another_order in binance_orders_at_exchange:
            if order == another_order:
                # we still have to check time and volume and price:
                if another_order.create_time >= order.create_time and \
                    abs(another_order.create_time - order.create_time) < 10 and \
                    abs(another_order.volume - order.volume) < 0.00001 and \
                        abs(another_order.price - order.price) < 0.00001:
                    found = True
                    orders_to_check.append(another_order)

        if not found:
            msg = "Cant found order registered at exchange {o}".format(o=order)
            log_to_file(msg, "orders_not_registered_at_binance.log")

    for order in orders_to_check:
        if order.executed_volume == 0.0:
            continue

        # DBG
        # if order.pair_id == 23:
        #    raise

        msg = """STARTED for order - {wtf}
        LAST_ID is {lid}
        """.format(wtf=order, lid=last_trade_idx[order.pair_id])
        log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")

        list_to_check = binance_trades_group_by_pair[order.pair_id][last_trade_idx[order.pair_id]:]

        if len(list_to_check) == 0:
            msg = """LENGTH IS ZERO
                current order: {o}
                current last_id - {lid}
                PREV list:""".format(o=order, lid=last_trade_idx[order.pair_id])
            log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")
            for twt in binance_trades_group_by_pair[order.pair_id]:
                log_to_file(twt, get_pair_name_by_id(order.pair_id) + ".txt")
            
            assert 0 == len(list_to_check)

        total_volume = float(0.0)
        cur_trade_list = []

        for trade in list_to_check:
            
            if trade.create_time < order.create_time:
                # In case SOMEONE put manual orders we have to take it into account
                last_trade_idx[order.pair_id] += 1
                msg = "SKIPPING TRADE BECAUSE OF TIME - {ttt}".format(ttt=trade)
                log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")

                continue 

            if abs(order.executed_volume - total_volume) > 0:

                last_trade_idx[order.pair_id] += 1

                total_volume += trade.volume
                cur_trade_list.append(trade)

                msg = """ADD NEW TRADE - {o}
                    LAST_ID NOW IS {lid}
                    total_volume = {tv}
                    order.executed_volume = {ev}
                    WTF = {wtf}
                    DIFF: {wtf1}
                    """.format(o=trade, lid=last_trade_idx[order.pair_id], tv=total_volume, ev=order.executed_volume,
                               wtf=order.executed_volume > total_volume, wtf1=order.executed_volume - total_volume)
                log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")

                if total_volume - order.executed_volume > 0.000001:
                    msg = """current order: {o}
                                    current last_id - {lid}
                                    volume_diff: {vd}
                                    PREV list:""".format(o=order, lid=last_trade_idx[order.pair_id],vd=float_to_str(total_volume - order.executed_volume))
                    log_to_file(msg, get_pair_name_by_id(order.pair_id) + ".txt")
                    for twt in binance_trades_group_by_pair[order.pair_id]:
                        log_to_file(twt, get_pair_name_by_id(order.pair_id) + ".txt")
                    print "YOUR PROBLEM IS ", order.pair_id, get_pair_name_by_id(order.pair_id)

                    assert total_volume - order.executed_volume > 0.000001

            # floating point arithmetic in python behind good and bad
            if abs(order.executed_volume - total_volume) <= 0.00000001:
                log_to_file("SHOULD BE ENOUGH VOLUME", get_pair_name_by_id(order.pair_id) + ".txt")
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
