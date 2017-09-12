from constants import BITTREX_CANCEL_ORDER, BITTREX_BUY_ORDER, BITTREX_SELL_ORDER
from data_access.internet import send_request


def add_buy_order_bittrex(key, pair_name, price, amount):
	# https://bittrex.com/api/v1.1/market/buylimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
    	final_url = BITTREX_BUY_ORDER + key + "&market=" + pair_name + "&quantity=" + str(amount) + "&rate=" + str(price)

    	if should_print_debug():
        	print final_url

	err_msg = "add_buy_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)
	r = send_request(final_url, err_msg)

	# FIXME
	print r

def add_sell_order_bittrex(key, pair_name, price, amount):
	# https://bittrex.com/api/v1.1/market/selllimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
	final_url = BITTREX_SELL_ORDER + key + "&market=" + pair_name + "&quantity=" + str(amount) + "&rate=" + str(price)

    	if should_print_debug():
        	print final_url

	err_msg = "add_sell_order bittrex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)
	r = send_request(final_url, err_msg)

	# FIXME
	print r

	
def cancel_order_bittrex(key, deal_id):
	# https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
	final_url = BITTREX_CANCEL_ORDER + key + "&uuid=" + deal_id

    	if should_print_debug():
        	print final_url

	err_msg = "cancel bittrex order with id {id}".format(id=deal_id)
	r = send_request(final_url, err_msg)

	# FIXME
	print r
