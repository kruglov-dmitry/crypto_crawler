from constants import KRAKEN_BASE_API_URL, KRAKEN_CANCEL_ORDER

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
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

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res



