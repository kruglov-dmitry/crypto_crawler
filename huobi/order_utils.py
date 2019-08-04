from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_DEAL_TIMEOUT, HUOBI_GET_OPEN_ORDERS, HUOBI_API_URL, \
    HUOBI_API_ONLY, HUOBI_GET_HEADERS
from huobi.error_handling import is_error


from data.trade import Trade

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_get_request_with_header

from debug_utils import ERROR_LOG_FILE_NAME, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME

from enums.status import STATUS

from utils.file_utils import log_to_file
from utils.key_utils import sign_string_256_base64
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

    res = PostRequestDetails(final_url, HUOBI_GET_HEADERS, params)

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
        status_code, orders = get_orders_huobi_result_processor(res, pair_name)

    return status_code, orders


def get_orders_huobi_result_processor(json_document, pair_name):
    """
    Used to parse result for order_history and open_orders end points

    :param json_document - response from exchange api as json string
    :param pair_name - for backwards capabilities

    :return pair of status code, result
    """

    orders = []
    if is_error(json_document) or "data" not in json_document:
        msg = "get_open_orders_huobi_result_processor - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return STATUS.FAILURE, orders

    for entry in json_document["data"]:
        order = Trade.from_huobi(entry, pair_name)
        if order is not None:
            orders.append(order)

    return STATUS.SUCCESS, orders
