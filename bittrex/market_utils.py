from urllib import urlencode as _urlencode

from data_access.classes.PostRequestDetails import PostRequestDetails

from bittrex.constants import BITTREX_CANCEL_ORDER, BITTREX_NUM_OF_DEAL_RETRY, BITTREX_DEAL_TIMEOUT

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_TRACE
from utils.key_utils import signed_string
from utils.file_utils import log_to_file

from data_access.memory_cache import generate_nonce
from data_access.internet import send_post_request_with_header


def cancel_order_bittrex(key, order_id):
    # https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
    final_url = BITTREX_CANCEL_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "uuid": order_id,
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    post_details = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "cancel_order_bittrex: {res}".format(res=post_details)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel bittrex order with id {id}".format(id=order_id)

    res = send_post_request_with_header(post_details, err_msg, max_tries=BITTREX_NUM_OF_DEAL_RETRY,
                                        timeout=BITTREX_DEAL_TIMEOUT)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_bittrex(http_responce):
    if get_logging_level() >= LOG_ALL_TRACE:
        log_to_file("bittrex\n" + str(http_responce), "parse_id.log")
        try:
            log_to_file("bittrex\n" + str(http_responce.json()), "parse_id.log")
        except:
            pass

    if http_responce.status_code == 200:
        json_document = http_responce.json()
        return parse_order_id_bittrex_from_json(json_document)

    return None


def parse_order_id_bittrex_from_json(json_document):
    """
    {u'message': u'',
        u'result': {
            u'uuid': u'b818589b-f799-476d-9b9c-71bc1ac5c653'},
        u'success': True
    }
    """
    if json_document is not None and "result" in json_document and "uuid" in json_document["result"]:
        return json_document["result"]["uuid"]

    return None
