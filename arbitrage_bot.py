from dao.dao import get_order_book, buy_by_exchange, sell_by_exchange
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from file_parsing import init_pg_connection, load_to_postgres
from utils.key_utils import load_keys
from debug_utils import should_print_debug
from utils.time_utils import sleep_for
from core.base_analysis import get_change
from core.base_math import get_all_combination
from enums.currency_pair import CURRENCY_PAIR
from enums.deal_type import DEAL_TYPE
from collections import defaultdict
from data.Trade import Trade
from data.OrderBook import OrderBook
from enums.exchange import EXCHANGE

# time to poll - 2 MINUTES
POLL_PERIOD_SECONDS = 120


# FIXME NOTES:
# 1. load initial balance to know what I can afford to buy
# 2. load current deals set?
# 3. integrate to bot commands to show active deal and be able to cancel them by command in chat?
# 4. take into account that we may need to change frequency of polling based on prospectivness of currency pair


def balance_init():
    # FIXME TODO
    pass


def balance_adjust(order_book_pairs, balance_adjust_threshold, balance):
    # FIXME perform deal in case balance_adjust_threshold is reached
    # do reverse deal here
    pass


def dummy_balance_init(currency_pairs, default_volume):
    # FIXME
    pass


def init_deal(trade_to_perform, debug_msg):
    try:
        if trade_to_perform.deal_type == DEAL_TYPE.SELL:
            buy_by_exchange(trade_to_perform)
        else:
            sell_by_exchange(trade_to_perform)
    except Exception, e:
        print "init_deal: failed with following exception: ", str(e), debug_msg


def analyse_order_book(first_order_book, second_order_book, threshold, action_to_perform):

    if len(first_order_book.bid) == 0 or len(second_order_book.ask) == 0:
        return

    difference = get_change(first_order_book.bid[0].price, second_order_book.ask[-1].price, provide_abs=False)

    if should_print_debug():
        print "check_highest_bid_bigger_than_lowest_ask"
        print "ASK: ", first_order_book.bid[0].price
        print "BID: ", second_order_book.ask[-1].price
        print "DIFF: ", difference

    if difference >= threshold:
        # FIXME do we have enough volume of this currency to sell?
        # FIXME do we have enough volume of WHAT currency to buy
        # FIXME NOTE think about splitting on sub-methods for beatification

        msg = "highest bid bigger than Lowest ask for more than {num} %".format(num=threshold)

        min_volume = min(first_order_book.bid[0].volume, second_order_book.ask[0].volume)

        trade_at_first_exchange = Trade(DEAL_TYPE.SELL,
                                        first_order_book.exchange_id,
                                        first_order_book.pair_id,
                                        first_order_book.bid[0].price,
                                        min_volume)
        action_to_perform("history_trades.txt", trade_at_first_exchange)

        trade_at_second_exchange = Trade(DEAL_TYPE.BUY,
                                         second_order_book.exchange_id,
                                         second_order_book.pair_id,
                                         second_order_book.ask[0].price,
                                         min_volume)
        action_to_perform("history_trades.txt", trade_at_second_exchange)

        # adjust volumes
        if first_order_book.bid[0].volume > min_volume:
            first_order_book.bid[0].volume = first_order_book.bid[0].volume - min_volume
            second_order_book.ask = second_order_book.ask[:-1]
        elif second_order_book.ask[0].volume > min_volume:
            second_order_book.ask[0].volume = first_order_book.ask[0].volume - min_volume
            first_order_book.bid = first_order_book.bid[1:]

        # continue processing remaining order book
        analyse_order_book(first_order_book, second_order_book, threshold, action_to_perform)


def mega_analysis(order_book, threshold, balance_adjust_threshold, balance, action_to_perform):
    """
    :param order_book: dict of lists with order book, where keys are exchange names within particular time window
            either request timeout or by timest window during playing within database
    :param threshold: minimum difference of ask vs bid in percent that should trigger deal
    :param action_to_perform: method, that take details of ask bid at two exchange and trigger deals
    :return:
    """

    # split on currencies
    for every_currency in CURRENCY_PAIR.values():

        order_book_by_exchange_by_currency = defaultdict(list)

        for exchange_id in EXCHANGE.values():
            if exchange_id in order_book:
                exchange_order_book = [x for x in order_book[exchange_id] if x.pair_id == every_currency]

                # sort bids ascending and asks descending by price
                for x in exchange_order_book:
                    x.sort_by_price()

                order_book_by_exchange_by_currency[exchange_id] = exchange_order_book
            else:
                print "{0} exchange not present within order_book!".format(exchange_id)

        order_book_pairs = get_all_combination(order_book_by_exchange_by_currency, 2)

        for every_pair in order_book_pairs:
            # FIXME NOTE - recursion will change them so we need to re-init it to apply vise-wersa processing

            first_order_book = order_book_by_exchange_by_currency[every_pair[0]]
            second_order_book = order_book_by_exchange_by_currency[every_pair[1]]

            if len(first_order_book) > 1 or len(second_order_book) > 1:
                print "Something severely wrong!", len(first_order_book), len(second_order_book)
            
            analyse_order_book(first_order_book[0], second_order_book[0], threshold, action_to_perform)

            first_order_book = order_book_by_exchange_by_currency[every_pair[0]]
            second_order_book = order_book_by_exchange_by_currency[every_pair[1]]
            analyse_order_book(second_order_book[0], first_order_book[0], threshold, action_to_perform)

        balance.is_there_disbalance(every_currency, balance_adjust_threshold)
        # Big question - when to perform reverse deal
        balance_adjust(order_book_pairs, balance_adjust_threshold, balance)


def print_possible_deal_info(file_name, trade):
    with open(file_name, 'a') as the_file:
        the_file.write(str(trade) + "\n")


def get_time_entries(pg_conn):
    time_entries = []

    select_query = "select distinct timest from order_book"
    cursor = pg_conn.get_cursor()

    cursor.execute(select_query)

    for row in cursor:
        time_entries.append(row[0])

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


def run_analysis_over_db(deal_threshold, balance_adjust_threshold):
    # FIXME NOTE: accumulate profit

    pg_conn = init_pg_connection()
    time_entries = get_time_entries(pg_conn)
    time_entries_num = len(time_entries)
    print "Order_book num: ", time_entries_num 
    cnt = 0
    DEFAULT_VOLUME = 100

    current_balance = dummy_balance_init(CURRENCY_PAIR.values(), DEFAULT_VOLUME)

    for every_time_entry in time_entries:
        order_book_grouped_by_time = get_order_book_by_time(pg_conn, every_time_entry)

        # for x in order_book_grouped_by_time:
        mega_analysis(order_book_grouped_by_time, deal_threshold, balance_adjust_threshold, current_balance, print_possible_deal_info)
        cnt += 1
        print "Processed ", cnt, " out of ", time_entries_num, " time entries"


def run_bot(deal_threshold, balance_adjust_threshold):
    load_keys("./secret_keys")

    current_balance = balance_init()

    while True:
        order_book = get_order_book()

        mega_analysis(order_book, deal_threshold, balance_adjust_threshold, current_balance, init_deal)

        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    pg_conn = init_pg_connection()

    # FIXME - read from some config
    deal_threshold = 1.5
    balance_adjust_threshold = 5.0

    run_analysis_over_db(deal_threshold, balance_adjust_threshold)
