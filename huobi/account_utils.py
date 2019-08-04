from data_access.memory_cache import get_cache

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_get_request_with_header

from enums.status import STATUS

from huobi.constants import HUOBI_DEAL_TIMEOUT, HUOBI_ACOUNT_ID, HUOBI_GET_ACCOUNT_INFO, \
    HUOBI_API_URL, HUOBI_API_ONLY, HUOBI_GET_HEADERS
from huobi.rest_api import generate_body_and_url_get_request


def get_huobi_account_impl(key):

    final_url = HUOBI_API_URL + HUOBI_GET_ACCOUNT_INFO + "?"

    body, url = generate_body_and_url_get_request(key, HUOBI_API_ONLY, HUOBI_GET_ACCOUNT_INFO)
    final_url += url

    post_details = PostRequestDetails(final_url, HUOBI_GET_HEADERS, body)

    err_msg = "get_huobi_account"

    error_code, res = send_get_request_with_header(post_details.final_url, post_details.headers, err_msg,
                                                   timeout=HUOBI_DEAL_TIMEOUT)

    # {u'status': u'ok', u'data': [{u'subtype': u'', u'state': u'working', u'type': u'spot', u'id': 1245038}]}

    if error_code == STATUS.SUCCESS and "data" in res and len(res["data"]) > 0:
        return res["data"][0]["id"]

    return None


def get_huobi_account(key, cache=get_cache()):
    if cache.get_value(HUOBI_ACOUNT_ID) is None:
        huobi_account_id = get_huobi_account_impl(key)
        if huobi_account_id is not None:
            cache.set_value(HUOBI_ACOUNT_ID, huobi_account_id)
        else:
            assert huobi_account_id is not None
    return cache.get_value(HUOBI_ACOUNT_ID)
