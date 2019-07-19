from data_access.internet import send_get_request_with_header, send_delete_request_with_header

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    ERROR_LOG_FILE_NAME, LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from binance.constants import BINANCE_CANCEL_ORDER, BINANCE_DEAL_TIMEOUT, BINANCE_GET_ALL_TRADES
from binance.error_handling import is_error
from binance.rest_api import generate_post_request


def cancel_order_binance(key, pair_name, order_id):

    body = {
        "recvWindow": 5000,
        "timestamp": get_now_seconds_utc_ms(),
        "symbol": pair_name,
        "orderId": order_id
    }

    post_details = generate_post_request(BINANCE_CANCEL_ORDER, body, key)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "cancel_order_binance: url - {url} headers - {headers} body - {body}".format(
            url=post_details.final_url, headers=post_details.headers, body=post_details.body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel binance order with id {id}".format(id=order_id)

    res = send_delete_request_with_header(post_details, err_msg, max_tries=3)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_binance(json_document):
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

    if is_error(json_document):

        msg = "parse_order_id_binance - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    if "orderId" in json_document:
        return json_document["orderId"]

    return None


def get_trades_history_binance(key, pair_name, limit, last_order_id=None):
    final_url = BINANCE_GET_ALL_TRADES

    body = []

    if last_order_id is not None:
        body.append(("fromId", last_order_id))

    body.append(("symbol", pair_name))
    body.append(("limit", limit))
    body.append(("timestamp", get_now_seconds_utc_ms()))
    body.append(("recvWindow", 5000))
    body.append(("signature", signed_body_256(body, key.secret)))

    post_details = generate_post_request(final_url, body, key)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_trades_history_binance: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    err_msg = "get_all_trades_binance for {pair_name}".format(pair_name=pair_name)

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=BINANCE_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_all_trades_binance: {er_c} {r}".format(er_c=error_code, r=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    return error_code, res
