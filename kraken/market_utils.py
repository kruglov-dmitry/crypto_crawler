from kraken.constants import KRAKEN_BASE_API_URL, KRAKEN_CANCEL_ORDER, KRAKEN_NUM_OF_DEAL_RETRY, KRAKEN_DEAL_TIMEOUT

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level, \
    LOG_ALL_TRACE
from utils.key_utils import sign_kraken
from utils.file_utils import log_to_file

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce


def cancel_order_kraken(key, deal_id):
    # https://api.kraken.com/0/private/CancelOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CANCEL_ORDER

    body = {
        "txid": deal_id,
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CANCEL_ORDER, key.secret)}

    if should_print_debug():
        msg = "cancel_order_kraken: url - {url} headers - {headers} body - {body}".format(url=final_url,
                                                                                            headers=headers, body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel kraken called for {deal_id}".format(deal_id=deal_id)

    res = send_post_request_with_header(final_url, headers, body, err_msg,
                                        max_tries=KRAKEN_NUM_OF_DEAL_RETRY, timeout=KRAKEN_DEAL_TIMEOUT)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def parse_order_id_kraken(http_responce):
    if get_logging_level() >= LOG_ALL_TRACE:
        log_to_file("kraken\n" + str(http_responce), "parse_id.log")
        try:
            log_to_file("kraken\n" + str(http_responce.json()), "parse_id.log")
        except :
            pass

    if http_responce.status_code == 200:
        json_document = http_responce.json()
        return parse_order_id_kraken_from_json(json_document)

    return None


def parse_order_id_kraken_from_json(json_document):
    """
    {u'result': {u'descr':
            {u'order': u'sell 10.00000000 XMRXBT @ limit 0.045000'},
            u'txid': [u'OY3ZML-PE3LG-L4NG7C']},
    u'error': []}
    """

    if json_document is not None and 'result' in json_document and 'txid' in json_document['result']:
        return json_document['result']['txid']

    return None