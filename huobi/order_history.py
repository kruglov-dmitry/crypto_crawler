from urllib import urlencode as _urlencode

from utils.key_utils import sign_string_256_base64
from utils.time_utils import ts_to_string_utc, get_now_seconds_utc
from utils.file_utils import log_to_file
from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, LOG_ALL_DEBUG, \
    DEBUG_LOG_FILE_NAME, ERROR_LOG_FILE_NAME

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header
from data.trade import Trade

from huobi.constants import HUOBI_DEAL_TIMEOUT, HUOBI_ORDER_HISTORY_LIMIT, HUOBI_API_ONLY, HUOBI_GET_TRADE_HISTORY, \
    HUOBI_API_URL
from huobi.error_handling import is_error
from enums.status import STATUS


def get_order_history_huobi_post_details(key, pair_name, time_start, time_end, limit):
    """
        FIXME NOTE: limit can be used as well
    """
    final_url = HUOBI_API_URL + HUOBI_GET_TRADE_HISTORY + "?"

    # ('states', 'filled,partial-canceled'),

    ts1 = None
    ts2 = None
    if 0 < time_start <= time_end:
        ts1 = ts_to_string_utc(time_start, format_string='%Y-%m-%d')
        ts2 = ts_to_string_utc(time_end, format_string='%Y-%m-%d')

    body = [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S')),
            ('direct', '')]

    if ts1 is None or ts2 is None:
        body.append(('end-date', ''))
    else:
        body.append(('end-date', ts2))

    body.append(('from', ''))
    body.append(('size', ''))

    if ts1 is None or ts2 is None:
        body.append(('start-date', ''))
    else:
        body.append(('start-date', ts1))

    body.append(('states', 'filled,partial-canceled'))
    body.append(("symbol", pair_name))
    body.append(('types', ''))

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=HUOBI_GET_TRADE_HISTORY, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    params = {}

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    post_details = PostRequestDetails(final_url, headers, params)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get orders history huobi: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_huobi_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """
    orders = []
    if is_error(json_document) or 'data' not in json_document:

        msg = "get_order_history_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document["data"]:
        order = Trade.from_huobi(entry, pair_name)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders


def get_order_history_huobi(key, pair_name, time_start=0, time_end=get_now_seconds_utc(), limit=HUOBI_ORDER_HISTORY_LIMIT):

    post_details = get_order_history_huobi_post_details(key, pair_name, time_start, time_end, limit )

    err_msg = "get_all_orders_huobi for {pair_name}".format(pair_name=pair_name)

    status_code, json_responce = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                              timeout=HUOBI_DEAL_TIMEOUT)

    print json_responce

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_order_history_huobi: {sc} {resp}".format(sc=status_code, resp=json_responce)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    historical_orders = []
    if status_code == STATUS.SUCCESS:
        status_code, historical_orders = get_order_history_huobi_result_processor(json_responce, pair_name)

    return status_code, historical_orders
