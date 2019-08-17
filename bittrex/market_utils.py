from urllib import urlencode as _urlencode

from data_access.classes.post_request_details import PostRequestDetails

from bittrex.constants import BITTREX_CANCEL_ORDER, BITTREX_DEAL_TIMEOUT
from bittrex.error_handling import is_error

from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, ERROR_LOG_FILE_NAME
from utils.key_utils import signed_string
from utils.file_utils import log_to_file

from data_access.memory_cache import generate_nonce
from data_access.internet import send_get_request_with_header


def cancel_order_bittrex(key, order_id):
    # https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
    final_url = BITTREX_CANCEL_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "uuid": order_id,
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    post_details = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "cancel_order_bittrex: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel bittrex order with id {id}".format(id=order_id)

    res = send_get_request_with_header(post_details.final_url,
                                       post_details.headers,
                                       err_msg,
                                       timeout=BITTREX_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_bittrex(json_document):
    """
    {u'message': u'',
        u'result': {
            u'uuid': u'b818589b-f799-476d-9b9c-71bc1ac5c653'},
        u'success': True
    }
    """

    if is_error(json_document) or "uuid" not in json_document["result"]:

        msg = "parse_order_id_bittrex - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    return json_document["result"]["uuid"]