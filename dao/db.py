from collections import defaultdict

from data.order_book import OrderBook, ORDER_BOOK_INSERT_BIDS, ORDER_BOOK_INSERT_ASKS, ORDER_BOOK_TYPE_NAME
from data.trade import Trade
from data.candle import Candle

from data_access.classes.postgres_connection import PostgresConnection
from utils.time_utils import get_date_time_from_epoch
from utils.file_utils import log_to_file

from utils.debug_utils import print_to_console, LOG_ALL_ERRORS, ERROR_LOG_FILE_NAME, FAILED_ORDER_PROCESSING_FILE_NAME
from constants import START_OF_TIME

from enums.exchange import EXCHANGE


def log_error_query_failed(query, arg_list, exception):
    msg = "insert data failed for Query: {query} Args: {args} Exception: {excp}".format(
        query=query, args=arg_list, excp=str(exception))
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, ERROR_LOG_FILE_NAME)


def init_pg_connection(_db_host="192.168.1.106", _db_port=5432, _db_name="postgres"):
    pg_conn = PostgresConnection(db_host=_db_host, db_port=_db_port, db_name=_db_name, db_user="postgres",
                                 db_password="postgres")
    pg_conn.connect()
    return pg_conn


def insert_data(some_object, pg_conn, is_this_order_book):
    # NOTE commit should be after all inserts! ONCE
    cur = pg_conn.cursor

    PG_INSERT_QUERY = some_object.insert_query
    args_list = some_object.get_pg_arg_list()

    """
        args_list = re.split(';', every_line)
        args_list = [x.replace('\"','') for x in args_list]
        args_list[0] = int(args_list[0])
    """

    try:
        print "Inserting", some_object
        cur.execute(PG_INSERT_QUERY, args_list)
    except Exception, e:
        log_error_query_failed(PG_INSERT_QUERY, args_list, e)
        raise

    # Yeap, this crap I am not the biggest fun of!
    if is_this_order_book:
        try:
            res = cur.fetchone()
            order_book_id = res[0]

            for ask in some_object.ask:
                cur.execute(ORDER_BOOK_INSERT_ASKS, (order_book_id, ask.price, ask.volume))

            for bid in some_object.bid:
                cur.execute(ORDER_BOOK_INSERT_BIDS, (order_book_id, bid.price, bid.volume))
        except Exception, e:
            msg = "Insert data failed for order book exactly. Exception: {excp}".format(excp=str(e))
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, ERROR_LOG_FILE_NAME)


def load_to_postgres(array, pattern_name, pg_conn):

    dummy_flag = (pattern_name == ORDER_BOOK_TYPE_NAME)
    for entry in array:
        if entry:
            insert_data(entry, pg_conn, dummy_flag)

    pg_conn.commit()


def bulk_insert_to_postgres(pg_conn, table_name, column_names, array):
    from data_access.classes.file_iterator import IteratorFile

    cursor = pg_conn.cursor

    f = IteratorFile((x.tsv() for x in array))
    #
    #       Debug only
    #
    # log_to_file(table_name, table_name + ".txt")
    # log_to_file(column_names, table_name + ".txt")
    # for x in array:
    #    log_to_file(x.tsv(), table_name + ".txt")
    cursor.copy_from(f, table_name, columns=column_names)
    pg_conn.commit()


def save_alarm_into_pg(src_ticker, dst_ticker, pg_conn):
    cur = pg_conn.cursor

    PG_INSERT_QUERY = "insert into alarms(src_exchange_id, dst_exchange_id, src_pair_id, dst_pair_id, src_ask_price, " \
                      "dst_bid_price, timest, date_time) values(%s, %s, %s, %s, %s, %s, %s, %s);"
    args_list = (
        src_ticker.exchange_id,
        dst_ticker.exchange_id,
        src_ticker.pair_id,
        dst_ticker.pair_id,
        src_ticker.ask,
        dst_ticker.bid,
        src_ticker.timest,
        get_date_time_from_epoch(src_ticker.timest)
    )

    try:
        cur.execute(PG_INSERT_QUERY, args_list)
    except Exception, e:
        log_error_query_failed(PG_INSERT_QUERY, args_list, e)
    else:
        pg_conn.commit()


def get_time_entries(pg_conn):
    time_entries = []

    select_query = "select distinct timest from order_book order by timest asc"
    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        time_entries.append(long(row[0]))

    return time_entries


def get_order_book_asks(pg_conn, order_book_id):
    order_books_asks = []

    select_query = "select id, order_book_id, price, volume from order_book_ask where order_book_id = " + str(order_book_id)
    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        order_books_asks.append(row)

    return order_books_asks


def get_order_book_bids(pg_conn, order_book_id):
    order_books_bids = []

    select_query = "select id, order_book_id, price, volume from order_book_bid where order_book_id = " + str(order_book_id)
    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        order_books_bids.append(row)

    return order_books_bids


def get_order_book_by_time(pg_conn, timest):
    order_books = defaultdict(list)

    select_query = "select id, pair_id, exchange_id, timest from order_book where timest = " + str(timest)
    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        order_book_id = row[0]

        order_book_asks = get_order_book_asks(pg_conn, order_book_id)
        order_book_bids = get_order_book_bids(pg_conn, order_book_id)

        order_books[int(row[2])].append(OrderBook.from_row(row, order_book_asks, order_book_bids))

    return order_books


def get_arbitrage_id(pg_conn):
    cursor = pg_conn.cursor
    select_query = """select nextval('arbitrage_id_seq')"""
    cursor.execute(select_query)

    for row in cursor:
        return long(row[0])

    return None


def save_order_into_pg(order, pg_conn, table_name="arbitrage_orders"):
    cur = pg_conn.cursor

    PG_INSERT_QUERY = "insert into {table_name}(arbitrage_id, exchange_id, trade_type, pair_id, price, volume, " \
                      "executed_volume, order_id, trade_id, order_book_time, create_time, execute_time, execute_time_date) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);".format(table_name=table_name)
    args_list = (
        order.arbitrage_id,
        order.exchange_id,
        order.trade_type,
        order.pair_id,
        order.price,
        order.volume,
        order.executed_volume,
        order.order_id,
        order.trade_id,
        order.order_book_time,
        order.create_time,
        order.execute_time,
        get_date_time_from_epoch(order.execute_time)
    )

    try:
        cur.execute(PG_INSERT_QUERY, args_list)
    except Exception, e:
        log_error_query_failed(PG_INSERT_QUERY, args_list, e)
    else:
        pg_conn.commit()


def get_all_orders(pg_conn, table_name="arbitrage_orders", time_start=START_OF_TIME, time_end=START_OF_TIME):
    orders = []

    if time_start == START_OF_TIME and time_end == START_OF_TIME:
        select_query = """select arbitrage_id, exchange_id, trade_type, pair_id, price, volume, executed_volume,
        order_id, trade_id, order_book_time, create_time, execute_time from {table_name}""".format(table_name=table_name)
    else:
        select_query = """select arbitrage_id, exchange_id, trade_type, pair_id, price, volume, executed_volume,
        order_id, trade_id, order_book_time, create_time, execute_time from {table_name} where create_time >= {start_time}
        and create_time <= {end_time}
        """.format(table_name=table_name, start_time=time_start, end_time=time_end)

    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        orders.append(Trade.from_row(row))

    return orders


def is_order_present_in_order_history(pg_conn, trade, table_name="arbitrage_orders"):
    """
                We can execute history retrieval several times.
                Some exchanges do not have precise mechanism to exclude particular time range.
                It is possible to have multiple trades per order = order_id.
                As this is arbitrage it mean that all other fields may be the same.
                exchange_id | trade_type | pair_id |   price   |  volume    |   order_id | timest

                executed_volume

    :param pg_conn:
    :param trade:
    :param table_name:
    :return:
    """

    select_query = """select arbitrage_id, exchange_id, trade_type, pair_id, price, volume, executed_volume, order_id,
        trade_id, order_book_time, create_time, execute_time from {table_name} where order_id = '{order_id}'""".format(
        table_name=table_name, order_id=trade.order_id)

    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        cur_trade = Trade.from_row(row)
        if abs(cur_trade.executed_volume - trade.executed_volume) < 0.0000001 and \
                cur_trade.create_time == trade.create_time:
            return True

    return False


def is_trade_present_in_trade_history(pg_conn, trade, table_name="arbitrage_trades"):
    """
            For every order we can have multiple trades executed.
            In ideal case they all will be connected to the same order_id
            but not all exchange support it - Binance for example.

            Another tricky case python and how it deal with float point number and rounding

            So query below just an approximation to minimize possible duplicates

    :param pg_conn:
    :param trade:
    :param table_name:
    :return:
    """

    select_query = """select * from {table_name} where trade_id = '{trade_id}'""".format(
        table_name=table_name, trade_id=trade.trade_id)

    cursor = pg_conn.cursor

    cursor.execute(select_query)

    return cursor.rowcount > 0


def get_next_candidates(pg_conn, predicate):
    """
    :param pg_conn:
    :param predicate: method that should trigger retrieval of pair candles
    :return:
    """

    select_query = "select id, pair_id, exchange_id, open, close, high, low, timest, date_time from candle"

    cursor = pg_conn.cursor

    cursor.execute(select_query)

    prev = None
    for row in cursor:
        cur = Candle.from_row(row)
        if prev is None:
            prev = cur
            continue
        else:
            if predicate(cur.high, prev.low):
                yield cur, prev


def update_order_details(pg_conn, order):

    """
            if order.pair_id == every_order.pair_id and \
                        order.deal_type == every_order.deal_type and \
                        abs(order.price - every_order.price) < FLOAT_POINT_PRECISION and \
                        order.create_time >= every_order.create_time and \
                        abs(order.create_time - every_order.create_time) < 15:
            # FIXME
            order.order_id = every_order.order_id
            order.create_time = every_order.create_time


    :param pg_conn:
    :param order:
    :return:
    """

    select_query = """update arbitrage_orders set order_id = '{order_id}' where exchange_id = {e_id} and pair_id = {p_id} and
    trade_type = {d_type} and create_time = {c_time}
    """.format(order_id=order.order_id, e_id=order.exchange_id, p_id=order.pair_id, d_type=order.trade_type,
               c_time=order.create_time)

    cursor = pg_conn.cursor

    cursor.execute(select_query)

    if 0 == cursor.rowcount:
        msg = "ZERO number of row affected! For order = {o}".format(o=order)
        log_to_file(msg, FAILED_ORDER_PROCESSING_FILE_NAME)


def get_last_binance_trade(pg_conn, start_date, end_time, pair_id, table_name="arbitrage_trades"):

    select_query = """select arbitrage_id, exchange_id, trade_type, pair_id, price, volume, executed_volume, order_id,
    trade_id, order_book_time, create_time, execute_time from {table_name} where exchange_id = {exchange_id} and
    pair_id = {pair_id} and create_time >= {start_time} and create_time <= {end_time}
    ORDER BY create_time DESC limit 1""".format(
        table_name=table_name, exchange_id=EXCHANGE.BINANCE, pair_id=pair_id, start_time=start_date, end_time=end_time)

    cursor = pg_conn.cursor

    cursor.execute(select_query)

    for row in cursor:
        return Trade.from_row(row)

    return None
