from constants import KRAKEN_BASE_API_URL, KRAKEN_CANCEL_ORDER, KRAKEN_BUY_ORDER, KRAKEN_SELL_ORDER, \
    KRAKEN_CHECK_BALANCE, KRAKEN_GET_CLOSE_ORDERS, KRAKEN_GET_OPEN_ORDERS

from data_access.internet import send_post_request_with_header

from debug_utils import should_print_debug
from utils.key_utils import generate_nonce, sign_kraken
from utils.time_utils import get_now_seconds_local, sleep_for, get_now_seconds_utc
from utils.string_utils import float_to_str

from enums.exchange import EXCHANGE
from enums.status import STATUS

from data.Balance import Balance
from data.OrderState import OrderState
from data.Trade import Trade


def add_buy_order_kraken(key, pair_name, price, amount):

    print "add_buy_order_kraken - confirmation of deals via balance\order"
    raise

    max_retry_num = 3
    retry_num = 0

    error_code, res = STATUS.FAILURE, None

    # prev_num_of_orders = order_state.get_total_num_of_orders()

    while retry_num < max_retry_num:
        retry_num += 1

        error_code, res = add_buy_order_kraken_impl(key, pair_name, price, amount)

        if STATUS.FAILURE != error_code:
            return error_code, res

        # check whether we have added new deals
        # kraken may actually do it with some delay
        # lets try wait a bit to verify that they will not update it
        sleep_for(2)

        order_error_code, new_order_state = get_orders_kraken(key)

        if order_error_code == STATUS.SUCCESS:  # and prev_num_of_orders < new_order_state.get_total_num_of_orders():
            # FIXME well, ideally we have to look for pair_name, price and amount
            # But for now lets conclude that This crap did it!

            return STATUS.SUCCESS, res

        # otherwise - repeat
        sleep_for(1)

    return error_code, res


def add_buy_order_kraken_impl(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_BUY_ORDER

    current_nonce = generate_nonce()

    body = {
        "pair": pair_name,
        "type": "buy",
        "ordertype": "limit",
        "price": float_to_str(price),
        "volume": float_to_str(amount),
        "nonce": current_nonce
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_BUY_ORDER, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=1)     # FailFast motherfucker!

    if should_print_debug():
        print res

    return res


def add_sell_order_kraken(key, pair_name, price, amount):
    print "add_sell_order_kraken - confirmation of deals via balance\order"
    raise

    max_retry_num = 3
    retry_num = 0

    error_code, res = STATUS.FAILURE, None

    # prev_num_of_orders = order_state.get_total_num_of_orders()

    while retry_num < max_retry_num:
        retry_num += 1

        error_code, res = add_sell_order_kraken_impl(key, pair_name, price, amount)

        if STATUS.FAILURE != error_code:
            return error_code, res

        # check whether we have added new deals
        # kraken may actually do it with some delay
        # lets try wait a bit to verify that they will not update it
        sleep_for(2)

        order_error_code, new_order_state = get_orders_kraken(key)

        if order_error_code == STATUS.SUCCESS and prev_num_of_orders < new_order_state.get_total_num_of_orders():
            # FIXME well, ideally we have to look for pair_name, price and amount
            # But for now lets conclude that This crap did it!

            return STATUS.SUCCESS, res

        # otherwise - repeat
        sleep_for(1)

    return error_code, res


def add_sell_order_kraken_impl(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_SELL_ORDER

    current_nonce = generate_nonce()

    body = {
        "pair": pair_name,
        "type": "sell",
        "ordertype": "limit",
        "price": float_to_str(price),
        "volume": float_to_str(amount),
        "nonce": current_nonce
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_SELL_ORDER, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=1)

    if should_print_debug():
        print res

    return res


def cancel_order_kraken(key, deal_id):
    # https://api.kraken.com/0/private/CancelOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CANCEL_ORDER

    body = {
        "txid": deal_id,
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CANCEL_ORDER, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel kraken called for {deal_id}".format(deal_id=deal_id)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if should_print_debug():
        print res

    return res


def get_balance_kraken(key):
    """
    Example of request \ responce
        https://api.kraken.com/0/private/Balance
        {'API-Key': 'whatever',
         'API-Sign': u'whatever'}
        {'nonce': 1508503223939}

    Responce:
    {u'result': {u'DASH': u'33.2402410500', u'BCH': u'22.4980093900', u'ZUSD': u'12747.4370', u'XXBT': u'3.1387700870',
                 u'EOS': u'2450.8822990100', u'USDT': u'77.99709699', u'XXRP': u'0.24804100',
                 u'XREP': u'349.7839715600', u'XETC': u'508.0140331400', u'XETH': u'88.6104554900'}, u'error': []}
    """
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CHECK_BALANCE

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CHECK_BALANCE, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check kraken balance called"

    timest = get_now_seconds_utc()
    error_code, res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if error_code == STATUS.SUCCESS and "result" in res:
        res = Balance.from_kraken(timest, res["result"])

    return error_code, res


def ger_open_orders_kraken(key):
    """
     {
 	"result": {
 		"open": {
 			"OHBQIW-6R6XD-DKOE5J": {
 				"status": "open",
 				"fee": "0.00000000",
 				"expiretm": 0,
 				"descr": {
 					"leverage": "none",
 					"ordertype": "limit",
 					"price": "0.0002100",
 					"pair": "EOSXBT",
 					"price2": "0",
 					"type": "sell",
 					"order": "sell 1250.88000000 EOSXBT @ limit 0.0002100"
 				},
 				"vol": "1250.88000000",
 				"cost": "0.00000000",
 				"misc": "",
 				"price": "0.00000000",
 				"starttm": 0,
 				"userref": null,
 				"vol_exec": "0.00000000",
 				"oflags": "fciq",
 				"refid": null,
 				"opentm": 1509592448.2296
 			},
 		}
 	}
 }
    """


    final_url = KRAKEN_BASE_API_URL + KRAKEN_GET_OPEN_ORDERS

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_GET_OPEN_ORDERS, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check kraken open orders called"

    timest = get_now_seconds_utc()
    error_code, res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    open_orders = []
    if error_code == STATUS.SUCCESS and "result" in res:
        if "open" in res["result"]:
            for order_id in res["result"]["open"]:
                new_order = Trade.from_kraken(order_id, res["result"]["open"][order_id])
                if new_order is not None:
                    open_orders.append(new_order)

    return error_code, open_orders


def get_closed_orders_kraken(key):
    final_url = KRAKEN_BASE_API_URL + KRAKEN_GET_CLOSE_ORDERS

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_GET_CLOSE_ORDERS, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check kraken closed orders called"

    timest = get_now_seconds_utc()
    error_code, res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    closed_orders = []
    if error_code == STATUS.SUCCESS and "result" in res:
        if "closed" in res["result"]:
            for order_id in res["result"]["closed"]:
                new_order = Trade.from_kraken(order_id, res["result"]["closed"][order_id])
                if new_order is not None:
                    closed_orders.append(new_order)

    return error_code, closed_orders


def get_orders_kraken(key):

    timest = get_now_seconds_utc()
    error_code_1, open_orders = ger_open_orders_kraken(key)
    error_code_2, closed_orders = get_closed_orders_kraken(key)

    if error_code_1 == STATUS.FAILURE or error_code_2 == STATUS.FAILURE:
        return STATUS.FAILURE, None

    return STATUS.SUCCESS, OrderState(EXCHANGE.KRAKEN, timest, open_orders, closed_orders)
