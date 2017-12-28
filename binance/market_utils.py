from urllib import urlencode as _urlencode

from data_access.internet import send_get_request_with_header, send_delete_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from data.Trade import Trade

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, \
    LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc, get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from constants import BINANCE_CANCEL_ORDER, BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_OPEN_ORDERS
from enums.status import STATUS


def cancel_order_binance(key, pair_name, deal_id):

    final_url = BINANCE_CANCEL_ORDER

    body = {
        "recvWindow": 5000,
        "timestamp": get_now_seconds_utc(),
        "symbol": pair_name,
        "orderId": deal_id
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    if should_print_debug():
        msg = "cancel_order_binance: url - {url} headers - {headers} body - {body}".format(url=final_url,
                                                                                             headers=headers,
                                                                                             body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel binance order with id {id}".format(id=deal_id)

    res = send_delete_request_with_header(final_url, headers, {}, err_msg, max_tries=3)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
