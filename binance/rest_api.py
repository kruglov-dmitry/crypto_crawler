from urllib import urlencode as _urlencode

from data.trade import Trade
from data_access.classes.PostRequestDetails import PostRequestDetails
from utils.key_utils import signed_body_256

from utils.file_utils import log_to_file
from enums.status import STATUS
from debug_utils import ERROR_LOG_FILE_NAME

from binance.error_handling import is_error


def generate_post_request(final_url, body, key):
    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    # Yeah, body after that should be empty
    body = {}

    return PostRequestDetails(final_url, headers, body)


def get_orders_binance_result_processor(msg, json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """
    orders = []
    if is_error(json_document):
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document:
        order = Trade.from_binance(entry)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders
