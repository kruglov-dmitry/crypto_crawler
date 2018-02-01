from urllib import urlencode as _urlencode

from data_access.internet import send_delete_request_with_header

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_TRACE

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from binance.constants import BINANCE_CANCEL_ORDER, BINANCE_GET_ALL_ORDERS, BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_TRADES


def cancel_order_binance(key, pair_name, deal_id):

    final_url = BINANCE_CANCEL_ORDER

    body = {
        "recvWindow": 5000,
        "timestamp": get_now_seconds_utc_ms(),
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


def parse_deal_id_binance(http_responce):
    if get_logging_level() >= LOG_ALL_TRACE:
        log_to_file("binnace\n" + str(http_responce), "parse_id.log")
        try:
            log_to_file("binnace\n" + str(http_responce.json()), "parse_id.log")
        except:
            pass

    if http_responce.status_code == 200:
        json_document = http_responce.json()
        return parse_deal_id_binance_from_json(json_document)

    return None


def parse_deal_id_binance_from_json(json_document):
    """
    {u'orderId': 6599290,
    u'clientOrderId': u'oGDxv6VeLXRdvUA8PiK8KR',
    u'origQty': u'27.79000000',
    u'symbol': u'OMGBTC',
    u'side': u'SELL',
    u'timeInForce': u'GTC',
    u'status': u'FILLED',
    u'transactTime': 1514223327566,
    u'type': u'LIMIT',
    u'price': u'0.00111100',
    u'executedQty': u'27.79000000'}
    """

    if json_document is not None and "orderId" in json_document:
        return json_document["orderId"]

    return None


def get_order_history_for_time_interval_binance(key, pair_name, limit, last_order_id=None):
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


def get_trades_history_binance(key, pair_name, limit, last_order_id=None):
    final_url = BINANCE_GET_ALL_TRADES

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

    err_msg = "get_all_trades_binance for {pair_name}".format(pair_name=pair_name)

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    print "get_all_trades_binance", res

    return error_code, res