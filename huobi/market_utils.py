from urllib import urlencode as _urlencode

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, ERROR_LOG_FILE_NAME

from utils.key_utils import sign_string_256_base64
from utils.file_utils import log_to_file

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header

from huobi.constants import HUOBI_CANCEL_ORDER, HUOBI_DEAL_TIMEOUT, HUOBI_API_URL, HUOBI_API_ONLY, \
    HUOBI_NUM_OF_DEAL_RETRY
from huobi.error_handling import is_error


def cancel_order_huobi(key, pair_name, order_id):

    final_url = HUOBI_API_URL + HUOBI_CANCEL_ORDER + str(order_id) + "/submitcancel"

    body = []

    message = _urlencode(body).encode('utf8')

    msg = "POST\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=HUOBI_CANCEL_ORDER, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "cancel_order_huobi: url - {url} headers - {headers} body - {body}".format(
            url=final_url, headers=headers, body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel huobi order with id {id}".format(id=order_id)

    res = send_post_request_with_header(post_details, err_msg, max_tries=HUOBI_NUM_OF_DEAL_RETRY,
                                        timeout=HUOBI_DEAL_TIMEOUT)

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
