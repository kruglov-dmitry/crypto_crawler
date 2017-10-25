import sys
sys.setrecursionlimit(100)

from dao.dao import get_order_book, buy_by_exchange, sell_by_exchange, balance_init
from dao.db import init_pg_connection, load_to_postgres, get_order_book_by_time, get_time_entries

from utils.key_utils import load_keys
from debug_utils import should_print_debug
from utils.time_utils import sleep_for
from utils.currency_utils import split_currency_pairs, get_pair_name_by_id
from utils.exchange_utils import get_exchange_name_by_id

from core.base_analysis import get_change
from core.base_math import get_all_combination

from enums.exchange import EXCHANGE
from enums.currency_pair import CURRENCY_PAIR
from enums.deal_type import DEAL_TYPE

from collections import defaultdict

from data.OrderBook import ORDER_BOOK_TYPE_NAME
from data.Trade import Trade
from data.Balance import Balance
from data.BalanceState import BalanceState

from constants import ARBITRAGE_CURRENCY

# time to poll - 2 MINUTES
POLL_PERIOD_SECONDS = 120


# FIXME NOTE:
# This is indexes for comparison bid\ask within order books
# yeap, global constants is very bad
FIRST = 0
LAST = 0


# FIXME NOTES:
# 2. load current deals set?
# 3. integrate to bot commands to show active deal and be able to cancel them by command in chat?
# 4. take into account that we may need to change frequency of polling based on prospectivness of currency pair


def is_no_pending_order(currency_id, src_exchange_id, dst_exchange_id):
    # FIXME - have to load active deals per exchange >_<
    return True


def dummy_balance_init(timest, default_volume, balance_adjust_threshold):
    balance = {}

    initial_balance = {}

    for currency_id in ARBITRAGE_CURRENCY:
        initial_balance[currency_id] = default_volume

    for exchange_id in EXCHANGE.values():
        balance[exchange_id] = Balance(exchange_id, timest, initial_balance)

    return BalanceState(balance, balance_adjust_threshold)


def init_deal(trade_to_perform, debug_msg):
    try:
        if trade_to_perform.deal_type == DEAL_TYPE.SELL:
            buy_by_exchange(trade_to_perform)
        else:
            sell_by_exchange(trade_to_perform)
    except Exception, e:
        print "init_deal: failed with following exception: ", str(e), debug_msg


def determine_minimum_volume(first_order_book, second_order_book, disbalance_state):
    min_volume = min(first_order_book.bid[FIRST].volume, second_order_book.ask[LAST].volume)
    if min_volume < 0:
        print "analyse_order_book - something severely wrong - NEGATIVE min price: ", min_volume
        raise

    if not disbalance_state.do_we_have_enough_by_pair(first_order_book.pair_id,
                                                      first_order_book.exchange_id,
                                                      min_volume,
                                                      first_order_book.bid[FIRST].price
                                                      ):
        min_volume = disbalance_state.get_volume_by_pair_id(first_order_book.pair_id,
                                                            first_order_book.exchange_id)

    if not disbalance_state.do_we_have_enough_by_pair(second_order_book.pair_id,
                                                      second_order_book.exchange_id,
                                                      min_volume,
                                                      second_order_book.ask[LAST].price
                                                      ):
        min_volume = disbalance_state.get_volume_by_pair_id(second_order_book.pair_id,
                                                            second_order_book.exchange_id)

    return min_volume


def analyse_order_book(first_order_book, second_order_book, threshold, action_to_perform, disbalance_state, stop_recursion):

    if len(first_order_book.bid) == 0 or len(second_order_book.ask) == 0:
        return

    difference = get_change(first_order_book.bid[FIRST].price, second_order_book.ask[LAST].price, provide_abs=False)

    if should_print_debug():
        print "check_highest_bid_bigger_than_lowest_ask: BID = {bid} ASK = {ask}  DIFF = {diff}".format(
            bid=first_order_book.bid[FIRST].price, ask=second_order_book.ask[LAST].price, diff=difference)

    if difference >= threshold:
        # FIXME NOTE think about splitting on sub-methods for beatification

        msg = "highest bid bigger than Lowest ask for more than {num} %".format(num=threshold)

        min_volume = determine_minimum_volume(first_order_book, second_order_book, disbalance_state)

        trade_at_first_exchange = Trade(DEAL_TYPE.SELL,
                                        first_order_book.exchange_id,
                                        first_order_book.pair_id,
                                        first_order_book.bid[FIRST].price,
                                        min_volume)
        action_to_perform(trade_at_first_exchange, "history_trades.txt")

        # FIXME NOTE - should be performed ONLY after deal confirmation
        disbalance_state.add_balance_by_pair(first_order_book.pair_id,
                                             first_order_book.exchange_id,
                                             min_volume,
                                             first_order_book.bid[FIRST].price
                                             )

        trade_at_second_exchange = Trade(DEAL_TYPE.BUY,
                                         second_order_book.exchange_id,
                                         second_order_book.pair_id,
                                         second_order_book.ask[LAST].price,
                                         min_volume)
        action_to_perform(trade_at_second_exchange, "history_trades.txt")

        # FIXME NOTE - should be performed ONLY after deal confirmation
        disbalance_state.substract_balance_by_pair(second_order_book.pair_id,
                                                   second_order_book.exchange_id,
                                                   min_volume,
                                                   second_order_book.ask[LAST].price
                                                   )

        if len(first_order_book.bid) == 0 or len(second_order_book.ask) == 0:
            return
        # if len(first_order_book.bid) == 0 or len(second_order_book.ask) == 0 or \
        #   len(first_order_book.ask) == 0 or len(second_order_book.bid) == 0:
        #    return

        # adjust volumes
        if first_order_book.bid[FIRST].volume > min_volume:
            first_order_book.bid[FIRST].volume = first_order_book.bid[FIRST].volume - min_volume
            second_order_book.ask = second_order_book.ask[1:]
        elif second_order_book.ask[LAST].volume > min_volume:
            second_order_book.ask[LAST].volume = second_order_book.ask[LAST].volume - min_volume
            first_order_book.bid = first_order_book.bid[1:]

        if not stop_recursion:
            # continue processing remaining order book
            analyse_order_book(first_order_book,
                               second_order_book,
                               threshold,
                               action_to_perform,
                               disbalance_state,
                               stop_recursion)


def mega_analysis(order_book, threshold, disbalance_state, treshold_reverse, action_to_perform):
    """
    :param order_book: dict of lists with order book, where keys are exchange names within particular time window
            either request timeout or by timest window during playing within database
    :param threshold: minimum difference of ask vs bid in percent that should trigger deal
    :param disbalance_state
    :param treshold_reverse
    :param action_to_perform: method, that take details of ask bid at two exchange and trigger deals
    :return:
    """

    # split on currencies
    for currency_id in CURRENCY_PAIR.values():

        # we interested ONLY in arbitrage related coins
        src_coin, dst_coin = split_currency_pairs(currency_id)
        if src_coin not in ARBITRAGE_CURRENCY or \
                dst_coin not in ARBITRAGE_CURRENCY:
            continue

        order_book_by_exchange_by_currency = defaultdict(list)

        for exchange_id in EXCHANGE.values():
            if exchange_id in order_book:
                exchange_order_book = [x for x in order_book[exchange_id] if x.pair_id == currency_id]

                # sort bids ascending and asks descending by price
                for x in exchange_order_book:
                    x.sort_by_price()

                order_book_by_exchange_by_currency[exchange_id] = exchange_order_book
            else:
                print "{0} exchange not present within order_book!".format(exchange_id)

        order_book_pairs = get_all_combination(order_book_by_exchange_by_currency, 2)

        for every_pair in order_book_pairs:
            src_exchange_id = every_pair[0]
            dst_exchange_id = every_pair[1]

            # FIXME NOTE - recursion will change them so we need to re-init it to apply vise-wersa processing

            first_order_book = order_book_by_exchange_by_currency[src_exchange_id]
            second_order_book = order_book_by_exchange_by_currency[dst_exchange_id]

            if len(first_order_book) != 1 or len(second_order_book) != 1:
                print "mega_analysis: Something severely wrong!", len(first_order_book), len(second_order_book)
                print "For currency", get_pair_name_by_id(currency_id)
                print "For exchanges", get_exchange_name_by_id(src_exchange_id)
                print "For exchanges", get_exchange_name_by_id(dst_exchange_id)
                continue

            analyse_order_book(first_order_book[0],
                               second_order_book[0],
                               threshold,
                               action_to_perform,
                               disbalance_state,
                               stop_recursion=False)

            # FIXME NOTE - here we treat order book as unchanged, but it may already be affected by previous deals
            # previous call change bids of first order book & asks of second order book
            # but here we use oposite - i.e. should be fine
            # first_order_book = order_book_by_exchange_by_currency[src_exchange_id]
            # second_order_book = order_book_by_exchange_by_currency[dst_exchange_id]

            analyse_order_book(second_order_book[0],
                               first_order_book[0],
                               threshold,
                               action_to_perform,
                               disbalance_state,
                               stop_recursion=False)

            # FIXME NOTE
            # we need some mechanism to keep track of it!
            first_order_book = order_book_by_exchange_by_currency[src_exchange_id]
            second_order_book = order_book_by_exchange_by_currency[dst_exchange_id]

            # disbalance_state, treshold_reverse
            if disbalance_state.is_there_disbalance(currency_id,
                                                    src_exchange_id,
                                                    dst_exchange_id) and \
                    is_no_pending_order(currency_id, src_exchange_id, dst_exchange_id):
                analyse_order_book(second_order_book[0],
                                   first_order_book[0],
                                   treshold_reverse,
                                   action_to_perform,
                                   disbalance_state,
                                   stop_recursion=True)

            # FIXME NOTE - here we treat order book as unchanged, but it may already be affected by previous deals
            # previous call change bids of first order book & asks of second order book
            # but here we use oposite - i.e. should be fine
            first_order_book = order_book_by_exchange_by_currency[src_exchange_id]
            second_order_book = order_book_by_exchange_by_currency[dst_exchange_id]

            # disbalance_state, treshold_reverse
            if disbalance_state.is_there_disbalance(currency_id,
                                                    dst_exchange_id,
                                                    src_exchange_id
                                                    ) and \
                    is_no_pending_order(currency_id, dst_exchange_id, src_exchange_id):
                analyse_order_book(first_order_book[0],
                                   second_order_book[0],
                                   treshold_reverse,
                                   action_to_perform,
                                   disbalance_state,
                                   stop_recursion=True)


def print_possible_deal_info(trade, file_name):
    with open(file_name, 'a') as the_file:
        the_file.write(str(trade) + "\n")


def run_analysis_over_db(deal_threshold, balance_adjust_threshold, treshold_reverse):
    # FIXME NOTE: accumulate profit

    pg_conn = init_pg_connection()
    time_entries = get_time_entries(pg_conn)
    time_entries_num = len(time_entries)

    print "Order_book num: ", time_entries_num

    cnt = 0
    DEFAULT_VOLUME = 100000
    current_balance = dummy_balance_init(time_entries[0], DEFAULT_VOLUME, balance_adjust_threshold)
    for exch_id in current_balance.balance_per_exchange:
        print current_balance.balance_per_exchange[exch_id]

    for every_time_entry in time_entries:
        order_book_grouped_by_time = get_order_book_by_time(pg_conn, every_time_entry)

        # for x in order_book_grouped_by_time:
        mega_analysis(order_book_grouped_by_time,
                      deal_threshold,
                      current_balance,
                      treshold_reverse,
                      print_possible_deal_info)
        cnt += 1
        print "Processed ", cnt, " out of ", time_entries_num, " time entries"

    print "At the end of processing we have following balance:"
    print "NOTE: supposedly all buy \ sell request were fullfilled"
    for exch_id in current_balance.balance_per_exchange:
        print current_balance.balance_per_exchange[exch_id]


def run_bot(deal_threshold, balance_adjust_threshold, treshold_reverse):
    load_keys("./secret_keys")

    while True:
        order_book = get_order_book()

        current_balance = balance_init(balance_adjust_threshold)

        mega_analysis(order_book, deal_threshold, current_balance, treshold_reverse, init_deal)

        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    pg_conn = init_pg_connection()

    # FIXME - read from some config
    deal_threshold = 1.5
    treshold_reverse = 1.0
    balance_adjust_threshold = 5.0

    run_analysis_over_db(deal_threshold, balance_adjust_threshold, treshold_reverse)
