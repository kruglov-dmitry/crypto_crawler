from dao.dao import get_order_book
from data.OrderBook import ORDER_BOOK_TYPE_NAME
from file_parsing import init_pg_connection, load_to_postgres

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 900


def init_deal(exch_1_order, exch_2_order):
	# exchange specific >_<


# FIXME TODO - what if we add more exchanges
def mega_analysis(poloniex_order_book, kraken_order_book, bittrex_order_book, threshold):
	"""
		order_book is a tupple
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
		
		difference = get_change(pol_max.ask[0].price, krak_min.bid[0].price, provide_abs = False)
    		if should_print_debug():
    		    print "check_highest_bid_bigger_than_lowest_ask"
    		    print "ASK: ", pol_max.ask[0].price
    		    print "BID: ",  krak_min.bid[0].price
    		    print "DIFF: ", difference

    		if difference >= threshold:
    		    msg = "highest bid bigger than Lowest ask for more than {num} %".format(num=threshold)
		    # FIXME TODO init deal + recursive processing for next price
		    

if __name__ == "__main__":
    pg_conn = init_pg_connection()

    while (True):
	order_book = get_order_book(split_on_exchange=True)

	mega_analysis(order_book)

        load_to_postgres(order_book, ORDER_BOOK_TYPE_NAME, pg_conn)

        print "Before sleep..."
        sleep_for(POLL_PERIOD_SECONDS)
