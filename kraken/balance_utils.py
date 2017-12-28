from constants import KRAKEN_BASE_API_URL, KRAKEN_CHECK_BALANCE

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.key_utils import sign_kraken
from utils.time_utils import get_now_seconds_utc
from enums.status import STATUS

from data.Balance import Balance

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from data_access.PostRequestDetails import PostRequestDetails


def get_balance_kraken_post_details(key):
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CHECK_BALANCE

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CHECK_BALANCE, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_kraken_result_processor(json_document, timest):
    if json_document is not None and "result" in json_document:
        return Balance.from_kraken(timest, json_document["result"])

    return None


def get_balance_kraken(key):
    """
    Example of request \ responce
        https://api.kraken.com/0/private/Balance
        {'API-Key': 'whatever',
         'API-Sign': u'whatever'}
        {'nonce': 1508503223939}

    Responce:
    {u'result': {u'DASH': u'33.2402410500', u'BCH': u'22.4980093900', u'ZUSD': u'12747.4370', u'XXBT': u'3.1387700870',
                 u'EOS': u'2450.8822990100', u'USDT': u'77.99709699', u'XXRP': u'0.24804100',
                 u'XREP': u'349.7839715600', u'XETC': u'508.0140331400', u'XETH': u'88.6104554900'}, u'error': []}
    """

    post_details = get_balance_kraken_post_details(key)

    err_msg = "check kraken balance called"

    timest = get_now_seconds_utc()

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=1)

    if error_code == STATUS.SUCCESS and "result" in res:
        res = Balance.from_kraken(timest, res["result"])

    return error_code, res