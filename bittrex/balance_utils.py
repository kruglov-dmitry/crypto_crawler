from urllib import urlencode as _urlencode

from constants import BITTREX_CHECK_BALANCE, BITTREX_NUM_OF_DEAL_RETRY, BITTREX_DEAL_TIMEOUT
from data.Balance import Balance
from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from enums.status import STATUS
from utils.key_utils import signed_string
from utils.time_utils import get_now_seconds_utc


def get_balance_bittrex_post_details(key):
    final_url = BITTREX_CHECK_BALANCE + key.api_key + "&nonce=" + str(generate_nonce())

    body = {
    }

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_bittrex_result_processor(json_document, timest):
    if json_document is not None and "result" in json_document:
        return Balance.from_bittrex(timest, json_document["result"])

    return None


def get_balance_bittrex(key):
    """
        https://bittrex.com/api/v1.1/account/getbalances?apikey=8a2dd16465b0469197574ec0a516badb&nonce=1508507525325
        {'apisign': 'e6bfb1cc60dcd93d291542cf6c4084e942659be7c363633f710336338a3158b37eb3f999250e5113ffc9e48c18ebe24cf9f4d496f6348a319cbd7f1bc0fc680c'} {}
        {u'message': u'',
        u'result': [{u'Available': 21300.0, u'Currency': u'ARDR', u'Balance': 21300.0, u'Pending': 0.0,
        u'CryptoAddress': u'76730d86115b49b9b7f71578feb35b7da1ca6c13e5f745aa9b630707f5439e68'},

        {u'Available': 49704.04069438, u'Currency': u'BAT', u'Balance': 49704.04069438, u'Pending': 0.0,
        u'CryptoAddress': None},

        {u'Available': 0.0, u'Currency': u'BCC', u'Balance': 0.0, u'Pending': 0.0,
        u'CryptoAddress': u'1H24rzfFWy8thV1AYQch3GByrQQuXA65LY'},

        {u'Available': 0.28912516, u'Currency': u'BTC', u'Balance': 0.28912516, u'Pending': 0.0,
        u'CryptoAddress': u'1EJztGvnKbNj3GeFbt83HhsKeLBYeu8jGq'},

        {u'Available': 0.0, u'Currency': u'BTS', u'Balance': 0.0, u'Pending': 0.0, u'CryptoAddress': u'490d0054055c43ada6e'},

    """

    post_details = get_balance_bittrex_post_details(key)

    err_msg = "check bittrex balance called"

    timest = get_now_seconds_utc()

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg,
                                                    max_tries=BITTREX_NUM_OF_DEAL_RETRY,
                                                    timeout=BITTREX_DEAL_TIMEOUT)

    if error_code == STATUS.SUCCESS and "result" in res:
        res = Balance.from_bittrex(timest, res["result"])

    return error_code, res