from collections import defaultdict
from data.OrderBook import OrderBook, ORDER_BOOK_INSERT_BIDS, ORDER_BOOK_INSERT_ASKS, ORDER_BOOK_TYPE_NAME
from data_access.postgres_connection import PostgresConnection
from utils.time_utils import get_date_time_from_epoch


def init_pg_connection(_db_host="192.168.1.106"):
    # FIXME NOTE hardcoding is baaad Dmitry! pass some config
    pg_conn = PostgresConnection(db_host=_db_host, db_port=5432, db_name="postgres", db_user="postgres",
                                 db_password="postgres")
    pg_conn.connect()
    return pg_conn


def insert_data(some_object, pg_conn, dummy_flag):
    # NOTE commit should be after all inserts! ONCE
    cur = pg_conn.get_cursor()

    PG_INSERT_QUERY = some_object.insert_query
    args_list = some_object.get_pg_arg_list()

    """
        args_list = re.split(';', every_line)
        args_list = [x.replace('\"','') for x in args_list]
        args_list[0] = int(args_list[0])
    """

    try:
        cur.execute(PG_INSERT_QUERY, args_list)
    except Exception, e:
        print "insert data failed :(  ", str(e)

    # Yeap, this crap I am not the biggest fun of!
    if dummy_flag:
        try:
            res = cur.fetchone()
            order_book_id = res[0]

            for ask in some_object.ask:
                cur.execute(ORDER_BOOK_INSERT_ASKS, (order_book_id, ask.price, ask.volume))

            for bid in some_object.bid:
                cur.execute(ORDER_BOOK_INSERT_BIDS, (order_book_id, bid.price, bid.volume))
        except Exception, e:
            print "Insert data failed for order book exactly: ", str(e)


def load_to_postgres(array, pattern_name, pg_conn):

    dummy_flag = (pattern_name == ORDER_BOOK_TYPE_NAME)
    for entry in array:
        insert_data(entry, pg_conn, dummy_flag)

    pg_conn.commit()


def save_alarm_into_pg(src_ticker, dst_ticker, pg_conn):
    cur = pg_conn.get_cursor()

    PG_INSERT_QUERY = "insert into alarms(src_exchange_id, dst_exchange_id, src_pair_id, dst_pair_id, src_ask_price, dst_bid_price, timest, date_time) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s);"
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
        print "save_alarm_into_pg insert data failed :(  ", str(e)
        print "args: ", args_list

    pg_conn.commit()


def get_time_entries(pg_conn):
    time_entries = []

    select_query = "select distinct timest from order_book order by timest desc"
    cursor = pg_conn.get_cursor()

    cursor.execute(select_query)

    for row in cursor:
        time_entries.append(long(row[0]))

    return time_entries


def get_order_book_asks(pg_conn, order_book_id):
    order_books_asks = []

    select_query = "select id, order_book_id, price, volume from order_book_ask where order_book_id = " + str(order_book_id)
    cursor = pg_conn.get_cursor()

    cursor.execute(select_query)

    for row in cursor:
        order_books_asks.append(row)

    return order_books_asks


def get_order_book_bids(pg_conn, order_book_id):
    order_books_bids = []

    select_query = "select id, order_book_id, price, volume from order_book_bid where order_book_id = " + str(order_book_id)
    cursor = pg_conn.get_cursor()

    cursor.execute(select_query)

    for row in cursor:
        order_books_bids.append(row)

    return order_books_bids


def get_order_book_by_time(pg_conn, timest):
    order_books = defaultdict(list)

    select_query = "select id, pair_id, exchange_id, timest from order_book where timest = " + str(timest)
    cursor = pg_conn.get_cursor()

    cursor.execute(select_query)

    for row in cursor:
        order_book_id = row[0]

        order_book_asks = get_order_book_asks(pg_conn, order_book_id)
        order_book_bids = get_order_book_bids(pg_conn, order_book_id)

        order_books[int(row[2])].append(OrderBook.from_row(row, order_book_asks, order_book_bids))

    return order_books