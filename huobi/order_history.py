from urllib import urlencode as _urlencode

from utils.key_utils import sign_string_256_base64
from utils.time_utils import ts_to_string_utc, get_now_seconds_utc
from utils.file_utils import log_to_file
from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, LOG_ALL_DEBUG, \
    DEBUG_LOG_FILE_NAME

from enums.status import STATUS

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_get_request_with_header

from huobi.constants import HUOBI_DEAL_TIMEOUT, HUOBI_API_ONLY, HUOBI_GET_TRADE_HISTORY, \
    HUOBI_API_URL, HUOBI_GET_HEADERS
from huobi.rest_api import init_body
from huobi.order_utils import get_orders_huobi_result_processor


def get_order_history_huobi_post_details(key, pair_name, time_start, time_end):
    """
        NOTE: limit can be used as well
        limit=HUOBI_ORDER_HISTORY_LIMIT
    """
    final_url = HUOBI_API_URL + HUOBI_GET_TRADE_HISTORY + "?"

    # ('states', 'filled,partial-canceled'),

    ts1 = None
    ts2 = None
    if 0 < time_start <= time_end:
        ts1 = ts_to_string_utc(time_start, format_string='%Y-%m-%d')
        ts2 = ts_to_string_utc(time_end, format_string='%Y-%m-%d')

    body = init_body(key)
    body.append('direct', '')

    if ts1 is None or ts2 is None:
        body.append(('end-date', ''))
    else:
        body.append(('end-date', ts2))

    body.extend([('from', ''), ('size', '')])

    if ts1 is None or ts2 is None:
        body.append(('start-date', ''))
    else:
        body.append(('start-date', ts1))

    body.extend([
        ('states', 'filled,partial-canceled'),
        ("symbol", pair_name),
        ('types', '')])

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=HUOBI_GET_TRADE_HISTORY, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    params = {}

    post_details = PostRequestDetails(final_url, HUOBI_GET_HEADERS, params)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "get orders history huobi: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return post_details


def get_order_history_huobi(key, pair_name, time_start=0, time_end=get_now_seconds_utc()):

    post_details = get_order_history_huobi_post_details(key, pair_name, time_start, time_end)

    err_msg = "get_all_orders_huobi for {pair_name}".format(pair_name=pair_name)

    status_code, json_responce = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                              timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_order_history_huobi: {sc} {resp}".format(sc=status_code, resp=json_responce)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    historical_orders = []
    if status_code == STATUS.SUCCESS:
        status_code, historical_orders = get_orders_huobi_result_processor(json_responce, pair_name)

    return status_code, historical_orders
