from constants import KRAKEN_BASE_API_URL, KRAKEN_GET_CLOSE_ORDERS, KRAKEN_GET_OPEN_ORDERS

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.key_utils import sign_kraken
from utils.time_utils import get_now_seconds_utc
from utils.file_utils import log_to_file
from currency_utils import get_currency_pair_from_kraken

from enums.exchange import EXCHANGE
from enums.status import STATUS

from data.OrderState import OrderState
from data.Trade import Trade

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from data_access.PostRequestDetails import PostRequestDetails


def get_open_orders_kraken_post_details(key, pair_name=None):
    final_url = KRAKEN_BASE_API_URL + KRAKEN_GET_OPEN_ORDERS

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_GET_OPEN_ORDERS, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "ger_open_orders_kraken: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_kraken(key, pair_name=None):
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

    post_details = get_open_orders_kraken_post_details(key, pair_name=None)

    err_msg = "check kraken open orders called"

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=5)

    print "get_open_orders_kraken:", res
    open_orders = []
    if error_code == STATUS.SUCCESS and "result" in res:
        open_orders = get_open_orders_kraken_result_processor(res)

    if pair_name is not None:
        pair_id = get_currency_pair_from_kraken(pair_name)
        open_orders = [x for x in open_orders if x.pair_id == pair_id]

    return error_code, open_orders


def get_open_orders_kraken_result_processor(json_document):
    open_orders = []

    if json_document is not None and "open" in json_document["result"]:
        for order_id in json_document["result"]["open"]:
            new_order = Trade.from_kraken(order_id, json_document["result"]["open"][order_id])
            if new_order is not None:
                open_orders.append(new_order)

    return open_orders


def get_closed_orders_kraken_post_details(key, pair_name=None):
    final_url = KRAKEN_BASE_API_URL + KRAKEN_GET_CLOSE_ORDERS

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_GET_CLOSE_ORDERS, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "get_closed_orders_kraken: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_closed_orders_kraken(key, pair_name=None):

    post_details = get_closed_orders_kraken_post_details(key, pair_name)

    err_msg = "check kraken closed orders called"

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=5)

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
    error_code_1, open_orders = get_open_orders_kraken(key)
    error_code_2, closed_orders = get_closed_orders_kraken(key)

    if error_code_1 == STATUS.FAILURE or error_code_2 == STATUS.FAILURE:
        return STATUS.FAILURE, None

    return STATUS.SUCCESS, OrderState(EXCHANGE.KRAKEN, timest, open_orders, closed_orders)
