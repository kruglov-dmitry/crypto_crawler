from dao.db import get_all_orders
from enums.exchange import EXCHANGE


def find_order_bot_history(order_binance, order_bot_history):
    for order in order_bot_history:
        if order.deal_id == order_binance.deal_id:
            return order

    return None


def prepare_data(pg_conn, start_time):
    orders = get_all_orders(pg_conn, table_name="orders", time_start=start_time)
    binance_orders_at_bot = [x for x in orders if x.exchange_id == EXCHANGE.BINANCE]

    binance_orders_at_exchange = get_all_orders(pg_conn, table_name="binance_order_history", time_start=start_time)
    binance_orders_at_exchange.sort(key=lambda x: x.create_time, reverse=False)

    history_trades = get_all_orders(pg_conn, table_name="arbitrage_trades", time_start=start_time)

    binance_trades = [x for x in history_trades if x.exchange_id == EXCHANGE.BINANCE]
    binance_trades.sort(key=lambda x: x.create_time, reverse=False)

    for order_binance in binance_orders_at_exchange:
        order_bot = find_order_bot_history(order_binance, binance_orders_at_bot)
        if order_bot is not None:
            order_binance.arbitrage_id = order_bot.arbitrage_id

    return orders, history_trades, binance_trades, binance_orders_at_bot, binance_orders_at_exchange
