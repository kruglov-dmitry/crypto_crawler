from dao.dao import get_order_book
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from file_parsing import init_pg_connection, load_to_postgres
from utils.key_utils import load_keys
from debug_utils import should_print_debug
from utils.time_utils import sleep_for
from core.base_analysis import get_change
from enums.currency_pair import CURRENCY_PAIR

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 900


def init_deal(exch_1_order, exch_2_order):
    pass


    # exchange specific >_<
    # call by exchange buy sell & pray


# FIXME TODO - what if we add more exchanges
def mega_analysis(poloniex_order_book, kraken_order_book, bittrex_order_book, threshold):
    """
	:param poloniex_order_book:
	:param kraken_order_book:
	:param bittrex_order_book:
	:param threshold:
	:return:

    """
    # split on currencies
    for every_currency in CURRENCY_PAIR.values():
        pol = [x for x in poloniex_order_book if x.pair_id == every_currency]
        krak = [x for x in kraken_order_book if x.pair_id == every_currency]
        bittr = [x for x in bittrex_order_book if x.pair_id == every_currency]

        # sort bids and asks by price
        for x in pol:
            x.sort_by_price()

        for x in krak:
            x.sort_by_price()

        for x in bittr:
            x.sort_by_price()

        pol_max = pol[0] if pol else None
        krak_max = krak[0] if krak else None
        bittr_max = bittr[0] if bittr else None
		
        pol_min = pol[-1] if pol else None
        krak_min = krak[-1] if krak else None
        bittr_min = bittr[-1] if bittr else None

        # check for threshold for every pair in more proper fashion

        # FIXME 2 : for every pair permutations
        difference = get_change(pol_max.ask[0].price, krak_min.bid[0].price, provide_abs = False)

        if should_print_debug():
            print "check_highest_bid_bigger_than_lowest_ask"
            print "ASK: ", pol_max.ask[0].price
            print "BID: ",  krak_min.bid[0].price
            print "DIFF: ", difference

        if difference >= threshold:
            msg = "highest bid bigger than Lowest ask for more than {num} %".format(num=threshold)
            # FIXME TODO init deal + recursive processing for next price
            # or not recursive but bissect everything that fall above threshold?

if __name__ == "__main__":
    pg_conn = init_pg_connection()
    load_keys("./secret_keys")
    threshold = 100 #  FIXME

    while (True):
        poloniex_order_book, kraken_order_book, bittrex_order_book = get_order_book(split_on_exchange=True)

        mega_analysis(poloniex_order_book, kraken_order_book, bittrex_order_book, threshold)

        load_to_postgres(poloniex_order_book, ORDER_BOOK_TYPE_NAME, pg_conn)
        load_to_postgres(kraken_order_book, ORDER_BOOK_TYPE_NAME, pg_conn)
        load_to_postgres(bittrex_order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)
