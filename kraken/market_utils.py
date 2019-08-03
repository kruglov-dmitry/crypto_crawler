from kraken.constants import KRAKEN_BASE_API_URL, KRAKEN_CANCEL_ORDER, KRAKEN_NUM_OF_DEAL_RETRY, KRAKEN_DEAL_TIMEOUT
from kraken.error_handling import is_error

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, ERROR_LOG_FILE_NAME
from utils.key_utils import sign_kraken
from utils.file_utils import log_to_file

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from data_access.classes.post_request_details import PostRequestDetails


def cancel_order_kraken(key, order_id):
    # https://api.kraken.com/0/private/CancelOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CANCEL_ORDER

    body = {
        "txid": order_id,
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CANCEL_ORDER, key.secret)}

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "cancel_order_kraken: url - {url} headers - {headers} body - {body}".format(
            url=final_url, headers=headers, body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    post_details = PostRequestDetails(final_url, headers, body)

    err_msg = "cancel kraken called for {order_id}".format(order_id=order_id)

    res = send_post_request_with_header(post_details, err_msg, max_tries=KRAKEN_NUM_OF_DEAL_RETRY, timeout=KRAKEN_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_kraken(json_document):
    """
    {u'result': {u'descr':
            {u'order': u'sell 10.00000000 XMRXBT @ limit 0.045000'},
            u'txid': [u'OY3ZML-PE3LG-L4NG7C']},
    u'error': []}
    """

    if is_error(json_document):

        msg = "parse_order_id_kraken - error response - {er}".format(er=json_document)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        return None

    if 'txid' in json_document['result']:
        return json_document['result']['txid']

    return None