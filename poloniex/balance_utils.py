from data_access.memory_cache import generate_nonce

from data_access.internet import send_post_request_with_header
from data_access.PostRequestDetails import PostRequestDetails

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from constants import POLONIEX_CHECK_BALANCE, POLONIEX_NUM_OF_DEAL_RETRY, POLONIEX_DEAL_TIMEOUT
from utils.time_utils import get_now_seconds_utc

from data.Balance import Balance
from enums.status import STATUS

from utils.key_utils import signed_body


def get_balance_poloniex_post_details(key):
    body = {
        'command': 'returnCompleteBalances',
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CHECK_BALANCE

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_poloniex_result_processor(json_document, timest):
    if json_document is not None:
        return Balance.from_poloniex(timest, json_document)

    return None


def get_balance_poloniex(key):
    """
    https://poloniex.com/tradingApi
    {'Key': 'QN6SDFQG-XVG2CGG3-WDDG2WDV-VXZ7MYL3',
    'Sign': '368a800fcd4bc0f0d95151ed29c9f84ddf6cae6bc366d3105db1560318da72aa82281b5ea52f4d4ec929dd0eabc7339fe0e7dc824bf0f1c64e099344cd6e74d0'}
    {'nonce': 1508507033330, 'command': 'returnCompleteBalances'}

    {"LTC":{"available":"5.015","onOrders":"1.0025","btcValue":"0.078"},"NXT:{...} ... }

    """

    post_details = get_balance_poloniex_post_details(key)

    err_msg = "check poloniex balance called"

    timest = get_now_seconds_utc()
    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg,
                                                    max_tries=POLONIEX_NUM_OF_DEAL_RETRY,
                                                    timeout=POLONIEX_DEAL_TIMEOUT)

    if error_code == STATUS.SUCCESS:
        res = Balance.from_poloniex(timest, res)

    return error_code, res