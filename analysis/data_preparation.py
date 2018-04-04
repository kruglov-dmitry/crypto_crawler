from dao.db import get_all_orders
from enums.exchange import EXCHANGE


def find_order_bot_history(order_binance, order_bot_history):
    for order in order_bot_history:
        if order.order_id == order_binance.order_id:
            return order

    return None


def prepare_data(pg_conn, start_time, end_time):
    orders = get_all_orders(pg_conn, table_name="arbitrage_orders", time_start=start_time, time_end=end_time)

    history_trades = get_all_orders(pg_conn, table_name="arbitrage_trades", time_start=start_time, time_end=end_time)

    binance_trades = [x for x in history_trades if x.exchange_id == EXCHANGE.BINANCE]
    binance_trades.sort(key=lambda x: x.create_time, reverse=False)

    return orders, history_trades, binance_trades
