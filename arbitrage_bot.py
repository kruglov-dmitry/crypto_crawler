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
from enums.exchange import EXCHANGE

# time to poll - 2 MINUTES
POLL_PERIOD_SECONDS = 120


# FIXME NOTES:
# 1. load initial balance to know what I can afford to buy
# 2. load current deals set?
# 3. integrate to bot commands to show active deal and be able to cancel them by command in chat?
# 4. take into account that we may need to change frequency of polling based on prospectivness of currency pair


def init_deal(trade_to_perform, debug_msg):
    # FIXME try catch with debug msg

    if trade_to_perform.deal_type == DEAL_TYPE.SELL:
        buy_by_exchange(trade_to_perform)
    else:
        sell_by_exchange(trade_to_perform)


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

        trade_at_first_exchange = Trade(DEAL_TYPE.BUY,
                                        first_order_book.exchange_id,
                                        first_order_book.pair_id,
                                        first_order_book.bid[0].price,
                                        min_volume)
        action_to_perform(trade_at_first_exchange, msg)

        trade_at_second_exchange = Trade(DEAL_TYPE.SELL,
                                         second_order_book.exchange_id,
                                         second_order_book.pair_id,
                                         second_order_book.ask[0].price,
                                         min_volume)
        action_to_perform(trade_at_second_exchange, msg)

        # adjust volumes
        if first_order_book.bid[0].volume > min_volume:
            first_order_book.bid[0].volume = first_order_book.bid[0].volume - min_volume
            second_order_book.ask = second_order_book.ask[:-1]
        elif second_order_book.ask[0].volume > min_volume:
            second_order_book.ask[0].volume = first_order_book.ask[0].volume - min_volume
            first_order_book.bid = first_order_book.bid[1:]

        # continue processing remaining order book
        analyse_order_book(first_order_book, second_order_book, threshold, action_to_perform)


def mega_analysis(order_book, threshold, action_to_perform):
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
            analyse_order_book(first_order_book, second_order_book, threshold, action_to_perform)

            first_order_book = order_book_by_exchange_by_currency[every_pair[0]]
            second_order_book = order_book_by_exchange_by_currency[every_pair[1]]
            analyse_order_book(second_order_book, first_order_book, threshold, action_to_perform)


if __name__ == "__main__":
    pg_conn = init_pg_connection()
    load_keys("./secret_keys")

    threshold = 1.5 # FIXME

    while (True):
        order_book = get_order_book()

        mega_analysis(order_book, threshold, init_deal)

        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)
