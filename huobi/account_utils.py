from urllib import urlencode as _urlencode

from data_access.memory_cache import get_cache

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_get_request_with_header

from enums.status import STATUS

from utils.key_utils import sign_string_256_base64
from utils.time_utils import get_now_seconds_utc, ts_to_string_utc

from huobi.constants import HUOBI_DEAL_TIMEOUT, HUOBI_ACOUNT_ID, HUOBI_GET_ACCOUNT_INFO, HUOBI_API_URL, HUOBI_API_ONLY


def get_huobi_account_impl(key):

    final_url = HUOBI_API_URL + HUOBI_GET_ACCOUNT_INFO

    body = [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=HUOBI_GET_ACCOUNT_INFO, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    post_details = PostRequestDetails(final_url, headers, body)

    err_msg = "get_all_trades_huobi for {pair_name}"

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
