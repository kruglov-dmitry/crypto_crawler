from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_GET_ORDER_DETAILS, HUOBI_DEAL_TIMEOUT, HUOBI_GET_OPEN_ORDERS, HUOBI_API_URL, \
    HUOBI_API_ONLY
from huobi.error_handling import is_error


from data.Trade import Trade

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from debug_utils import ERROR_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME

from enums.status import STATUS
from enums.exchange import EXCHANGE

from utils.file_utils import log_to_file
from utils.key_utils import sign_string_256_base64, get_key_by_exchange
from utils.time_utils import ts_to_string_utc, get_now_seconds_utc


def get_open_orders_huobi_post_details(key, pair_name):
    final_url = HUOBI_API_URL + HUOBI_GET_OPEN_ORDERS + "?"

    # ('states', 'pre-submitted,submitted,partial-filled,partial-canceled'),

    body = [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S')),
            ('direct', ''),
            ('end_date', ''),
            ('from', ''),
            ('size', ''),
            ('start_date', ''),
            ('states', 'pre-submitted,submitted,partial-filled'),
            ("symbol", pair_name),
            ('types', '')
            ]

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=HUOBI_GET_OPEN_ORDERS, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    params = {}

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = PostRequestDetails(final_url, headers, params)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get_open_orders_huobi: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def get_open_orders_huobi(key, pair_name):
    post_details = get_open_orders_huobi_post_details(key, pair_name)

    err_msg = "get_orders_huobi"

    status_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                    timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_open_orders_huobi: {r}".format(r=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    orders = []
    if status_code == STATUS.SUCCESS:
        status_code, orders = get_open_orders_huobi_result_processor(res, pair_name)

    return status_code, orders


def update_filled_amount(order):
    url_path = HUOBI_GET_ORDER_DETAILS + order.order_id + "/matchresults"
    final_url = HUOBI_API_URL + url_path

    # NOTE: this is ugly hack to keep result_processor interface consistent
    key = get_key_by_exchange(EXCHANGE.HUOBI)

    body = [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=url_path, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    params = {}

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    request_details = PostRequestDetails(final_url, headers, params)

    err_msg = "{order}".format(order=order)

    status_code = STATUS.FAILURE
    while status_code == STATUS.FAILURE:
        status_code, json_responce = send_get_request_with_header(request_details.final_url, request_details.headers,
                                                                  err_msg, timeout=HUOBI_DEAL_TIMEOUT)
        if status_code == STATUS.SUCCESS and "data" in json_responce:
            order.executed_volume = long(json_responce["data"]["filled-amount"])
            break


def get_open_orders_huobi_result_processor(json_document, pair_name):
    """
    json_document - response from exchange api as json string
    pair_name - for backwords compabilities
    """

    orders = []
    if is_error(json_document) or "data" not in json_document:
        msg = "get_open_orders_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document["data"]:
        order = Trade.from_huobi(entry, pair_name)
        if order is not None:
            update_filled_amount(order)
            orders.append(order)

    return STATUS.SUCCESS, orders
