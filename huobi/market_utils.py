from urllib import urlencode as _urlencode

from data_access.internet import send_delete_request_with_header

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    ERROR_LOG_FILE_NAME, LOG_ALL_DEBUG, DEBUG_LOG_FILE_NAME

from utils.key_utils import signed_body_256
from utils.time_utils import get_now_seconds_utc_ms
from utils.file_utils import log_to_file

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from huobi.constants import HUOBI_CANCEL_ORDER, HUOBI_DEAL_TIMEOUT, HUOBI_GET_ALL_TRADES, HUOBI_ACOUNT_ID
from huobi.error_handling import is_error

from data_access.memory_cache import get_cache


def cancel_order_huobi(key, pair_name, order_id):

    final_url = HUOBI_CANCEL_ORDER + str(order_id) + "/submitcancel"

    body = {
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    body = {}

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "cancel_order_huobi: url - {url} headers - {headers} body - {body}".format(
            url=final_url, headers=headers, body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel huobi order with id {id}".format(id=order_id)

    res = send_delete_request_with_header(post_details, err_msg, max_tries=3)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_huobi(json_document):
    """
    {
        "status": "ok",
        "data": "59378"
    }
    """

    if is_error(json_document) or "data" not in json_document:

        msg = "parse_order_id_huobi - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    return json_document["data"]


def get_huobi_account(cache=get_cache()):
    if cache.get_value(HUOBI_ACOUNT_ID) is None:
        WTF
        cache.set_value(HUOBI_ACOUNT_ID, )
    return cache.get_value(HUOBI_ACOUNT_ID)


def get_trades_history_huobi(key, pair_name, limit, last_order_id=None):
    final_url = HUOBI_GET_ALL_TRADES

    body = {}

    FIXME

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_trades_history_huobi: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    err_msg = "get_all_trades_huobi for {pair_name}".format(pair_name=pair_name)

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        msg = "get_all_trades_huobi: {er_c} {r}".format(er_c=error_code, r=res)
        print_to_console(msg, LOG_ALL_DEBUG)
        log_to_file(msg, DEBUG_LOG_FILE_NAME)

    return error_code, res