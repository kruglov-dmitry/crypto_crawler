from constants import KRAKEN_CANCEL_ORDER, KRAKEN_BUY_ORDER, KRAKEN_SELL_ORDER
from data_access.internet import send_post_request_with_header

def generate_nonce():
	# nonce = always increasing unsigned 64 bit integer
	# otp = two-factor password (if two-factor enabled, otherwise not required)
	# FIXME - store in db
	pass

def signed_body(body):
	# FIXME
	# Message signature using HMAC-SHA512 of (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key
	pass

def add_buy_order_kraken(key, pair_name, price, amount):
	body = { 
		"pair": pair_name,
		"type": "buy",
		"ordertype": "market",
		"price": "price",
		"volume": "amount",
		"nonce": generate_nonce() 
		}
	headers = {"API-Key": key, "API-Sign": signed_body(body)}
	# https://poloniex.com/tradingApi
	final_url = KRAKEN_BUY_ORDER

    	if should_print_debug():
        	print final_url, headers, body

	err_msg = "add_buy_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

	r = send_post_request_with_header(final_url, headers, body, err_msg)

	print r

def add_sell_order_kraken(key, pair_name, price, amount):
	body = { 
		"pair": pair_name,
		"type": "sell",
		"ordertype": "market",
		"price": "price",
		"volume": "amount",
		"nonce": generate_nonce() 
		}
	headers = {"API-Key": key, "API-Sign": signed_body(body)}
	# https://poloniex.com/tradingApi
	final_url = KRAKEN_BUY_ORDER

    	if should_print_debug():
        	print final_url, headers, body

	err_msg = "add_sell_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

	r = send_post_request_with_header(final_url, headers, body, err_msg)

	print r

def cancel_order_kraken(key, deal_id):
	body = {
		"txid": deal_id
		"nonce": generate_nonce() 
		}

	headers = {"API-Key": key, "API-Sign": signed_body(body)}
	# https://poloniex.com/tradingApi
	final_url = KRAKEN_BUY_ORDER

    	if should_print_debug():
        	print final_url, headers, body

	err_msg = "cancel kraken called for {deal_id}".format(deal_id=deal_id)

	r = send_post_request_with_header(final_url, headers, body, err_msg)

	print r
