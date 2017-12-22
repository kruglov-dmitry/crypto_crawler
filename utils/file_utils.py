import sys
import os
import glob

from data.Candle import Candle, CANDLE_TYPE_NAME
from data.OrderBook import OrderBook, ORDER_BOOK_TYPE_NAME
from data.OrderHistory import OrderHistory, TRADE_HISTORY_TYPE_NAME
from data.Ticker import Ticker, TICKER_TYPE_NAME
from utils.time_utils import get_now_seconds_utc

from constants import LOGS_FOLDER


def constructor_selector(class_name, string_repr):
    if class_name == TICKER_TYPE_NAME:
        return Ticker.from_string(string_repr)
    elif class_name == CANDLE_TYPE_NAME:
        return Candle.from_string(string_repr)
    elif class_name == ORDER_BOOK_TYPE_NAME:
        return OrderBook.from_string(string_repr)
    elif class_name == TRADE_HISTORY_TYPE_NAME:
        return OrderHistory.from_string(string_repr)


def save_list_to_file(some_data, file_name):
    with open(file_name, "a") as myfile:
        for entry in some_data:
            myfile.write("%s\n" % str(entry))


def log_to_file(trade, file_name, log_dir=LOGS_FOLDER):
    full_file_path = log_dir + file_name
    with open(full_file_path, 'a') as the_file:
        ts = get_now_seconds_utc()
        pid = os.getpid()
        the_file.write(str(ts) + " : " + " PID: " + str(pid) + " " + str(trade) + "\n")


def load_crap_from_folder(folder_name, pattern_name, pg_conn):
    file_list = glob.glob(folder_name + pattern_name + '*.txt')
    for every_file in file_list:
        print "Processing file ", every_file
        array = load_data_from_file(every_file, pattern_name, pg_conn)
        # load_to_postgres(array, pattern_name, pg_conn)


def load_data_from_file(every_file, pattern_name, pg_conn):
    array = []
    dummy_flag = (pattern_name == ORDER_BOOK_TYPE_NAME)
    with open(every_file, "r") as ins:
        for line in ins:
            obj = constructor_selector(pattern_name, line)
            # insert_data(obj, pg_conn, dummy_flag)
            pg_conn.commit()
        #     array.append(constructor_selector(pattern_name, line))
        #     if len(array) >= 100000:
        #    	load_to_postgres(array, pattern_name, pg_conn)
        # 	array = []
    return array


if __name__ == "__main__":
    folder_name = sys.argv[1]

    pg_conn = None # init_pg_connection()

    file_name_patterns = [TICKER_TYPE_NAME, CANDLE_TYPE_NAME, TRADE_HISTORY_TYPE_NAME]
    # file_name_patterns = [ORDER_BOOK_TYPE_NAME]

    for every_pattern in file_name_patterns:
        load_crap_from_folder(folder_name, every_pattern, pg_conn)



