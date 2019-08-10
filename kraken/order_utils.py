from kraken.constants import KRAKEN_BASE_API_URL, KRAKEN_GET_OPEN_ORDERS, EMPTY_LIST
from kraken.error_handling import is_error
from kraken.order_history import get_order_history_kraken

from data.order_state import OrderState
from data.trade import Trade

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from utils.debug_utils import get_logging_level, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, ERROR_LOG_FILE_NAME

from enums.exchange import EXCHANGE
from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import sign_kraken
from utils.time_utils import get_now_seconds_utc


def get_open_orders_kraken_post_details(key, pair_name=None):
    final_url = KRAKEN_BASE_API_URL + KRAKEN_GET_OPEN_ORDERS

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_GET_OPEN_ORDERS, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
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

    status_code, res = send_post_request_with_header(post_details, err_msg, max_tries=5)

    open_orders = EMPTY_LIST
    if status_code == STATUS.SUCCESS:
        open_orders = get_open_orders_kraken_result_processor(res, pair_name)

    return status_code, open_orders


def get_open_orders_kraken_result_processor(json_document, pair_name):
    open_orders = EMPTY_LIST

    if is_error(open_orders) or "open" not in json_document["result"]:

        msg = "get_open_orders_kraken_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return open_orders

    for order_id in json_document["result"]["open"]:
        new_order = Trade.from_kraken(order_id, json_document["result"]["open"][order_id])
        if new_order is not None:
            open_orders.append(new_order)

    return open_orders


def get_orders_kraken(key):

    timest = get_now_seconds_utc()
    error_code_1, open_orders = get_open_orders_kraken(key)
    error_code_2, closed_orders = get_order_history_kraken(key)

    if error_code_1 == STATUS.FAILURE or error_code_2 == STATUS.FAILURE:
        return STATUS.FAILURE, None

    return STATUS.SUCCESS, OrderState(EXCHANGE.KRAKEN, timest, open_orders, closed_orders)
