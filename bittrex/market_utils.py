from urllib import urlencode as _urlencode

from constants import BITTREX_CANCEL_ORDER, BITTREX_BUY_ORDER, BITTREX_SELL_ORDER, BITTREX_CHECK_BALANCE, \
    BITTREX_NUM_OF_DEAL_RETRY, BITTREX_DEAL_TIMEOUT, BITTREX_GET_OPEN_ORDERS

from data.Balance import Balance
from data.Trade import Trade

from enums.status import STATUS

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP, \
    LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.time_utils import get_now_seconds_utc
from utils.key_utils import signed_string
from utils.file_utils import log_to_file

from data_access.memory_cache import generate_nonce
from data_access.internet import send_post_request_with_header
from data_access.PostRequestDetails import PostRequestDetails


def cancel_order_bittrex(key, deal_id):
    # https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
    final_url = BITTREX_CANCEL_ORDER + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
        "uuid": deal_id,
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    if should_print_debug():
        msg = "cancel_order_bittrex: url - {url} headers - {headers} body - {body}".format(url=final_url,
                                                                                            headers=headers, body=body)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    err_msg = "cancel bittrex order with id {id}".format(id=deal_id)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
