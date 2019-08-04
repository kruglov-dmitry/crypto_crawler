from kraken.constants import KRAKEN_BASE_API_URL, KRAKEN_GET_CLOSE_ORDERS
from kraken.error_handling import is_error
from kraken.constants import EMPTY_LIST

from data.trade import Trade

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import get_logging_level, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, ERROR_LOG_FILE_NAME

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import sign_kraken
from utils.time_utils import get_now_seconds_utc


def get_closed_orders_kraken_post_details(key, pair_name=None, time_start=0, time_end=get_now_seconds_utc()):
    final_url = KRAKEN_BASE_API_URL + KRAKEN_GET_CLOSE_ORDERS

    body = {
        "nonce": generate_nonce(),
        "start": time_start,
        "end": time_end
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_GET_CLOSE_ORDERS, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_closed_orders_kraken: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_order_history_kraken_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """

    orders = EMPTY_LIST

    if is_error(json_document) or "closed" not in json_document["result"]:

        msg = "get_order_history_kraken_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return orders

    for order_id in json_document["result"]["closed"]:
        new_order = Trade.from_kraken(order_id, json_document["result"]["closed"][order_id])
        if new_order is not None:
            orders.append(new_order)

    return orders


def get_order_history_kraken(key, pair_name=None, time_start=0, time_end=get_now_seconds_utc()):

    post_details = get_closed_orders_kraken_post_details(key, pair_name, time_start, time_end)

    err_msg = "check kraken closed orders called"

    error_code, json_document = send_post_request_with_header(post_details, err_msg, max_tries=5)

    closed_orders = EMPTY_LIST
    if error_code == STATUS.SUCCESS:
        closed_orders = get_order_history_kraken_result_processor(json_document, pair_name)

    return error_code, closed_orders
