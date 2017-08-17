import sys
import glob
from data_access.postgres_connection import PostgresConnection

from data.Candle import Candle, CANDLE_TYPE_NAME
from data.OrderBook import OrderBook, ORDER_BOOK_TYPE_NAME, ORDER_BOOK_INSERT_BIDS, ORDER_BOOK_INSERT_ASKS
from data.OrderHistory import OrderHistory, TRADE_HISTORY_TYPE_NAME
from data.Ticker import Ticker, TICKER_TYPE_NAME


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

    cur.execute(PG_INSERT_QUERY, args_list)

    # Yeap, this crap I am not the biggest fun of!
    if dummy_flag:
        res = cur.fetchone()
        order_book_id = res[0]
        
        for ask in some_object.ask:
            cur.execute(ORDER_BOOK_INSERT_ASKS, (order_book_id, ask.price, ask.volume))

        for bid in some_object.bid:
            cur.execute(ORDER_BOOK_INSERT_BIDS, (order_book_id, bid.price, bid.volume))


def constructor_selector(class_name, string_repr):
    if class_name == TICKER_TYPE_NAME:
        return Ticker.from_string(string_repr)
    elif class_name == CANDLE_TYPE_NAME:
        return Candle.from_string(string_repr)
    elif class_name == ORDER_BOOK_TYPE_NAME:
        return OrderBook.from_string(string_repr)
    elif class_name == TRADE_HISTORY_TYPE_NAME:
        return OrderHistory.from_string(string_repr)

def load_data_from_file(every_file, pattern_name):
    array = []
    with open(every_file, "r") as ins:
        for line in ins:
            array.append(constructor_selector(pattern_name, line))
    return array

def load_to_postgres(array, pattern_name, pg_conn):

    dummy_flag = (pattern_name == ORDER_BOOK_TYPE_NAME)
    for entry in array:
        insert_data(entry, pg_conn, dummy_flag)

    pg_conn.commit()


def load_crap_from_folder(folder_name, pattern_name, pg_conn):
    file_list = glob.glob(folder_name + pattern_name + '*.txt')
    for every_file in file_list:
	print "Processing file ", every_file
        array = load_data_from_file(every_file, pattern_name)
        load_to_postgres(array, pattern_name, pg_conn)

def init_pg_connection():
    # FIXME NOTE hardcoding is baaad Dmitry! pass some config
    pg_conn = PostgresConnection(db_host="192.168.1.106", db_port=5432, db_name="postgres", db_user="postgres",
                                 db_password="postgres")
    pg_conn.connect()
    return pg_conn

if __name__ == "__main__":
    folder_name = sys.argv[1]

    pg_conn = init_pg_connection()

    # file_name_patterns = [TICKER_TYPE_NAME, CANDLE_TYPE_NAME, ORDER_BOOK_TYPE_NAME, TRADE_HISTORY_TYPE_NAME]
    file_name_patterns = [ORDER_BOOK_TYPE_NAME]

    for every_pattern in file_name_patterns:
        load_crap_from_folder(folder_name, every_pattern, pg_conn)
