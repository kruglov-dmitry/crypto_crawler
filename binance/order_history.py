from urllib import urlencode as _urlencode

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from binance.constants import BINANCE_GET_ALL_ORDERS, BINANCE_DEAL_TIMEOUT


def get_order_history_binance(key, pair_name, limit, last_order_id=None):
    final_url = BINANCE_GET_ALL_ORDERS

    if last_order_id is not None:
        body = {
            "symbol": pair_name,
            "limit": limit,
            "orderId": last_order_id,
            "timestamp": get_now_seconds_utc_ms(),
            "recvWindow": 5000
        }
    else:
        body = {
            "symbol": pair_name,
            "limit": limit,
            "timestamp": get_now_seconds_utc_ms(),
            "recvWindow": 5000
        }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    # Yeah, body after that should be empty
    body = {}

    post_details = PostRequestDetails(final_url, headers, body)

    err_msg = "get_all_orders_binance for {pair_name}".format(pair_name=pair_name)

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    print "get_open_orders_binance", res

    return error_code, res