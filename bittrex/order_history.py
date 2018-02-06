from urllib import urlencode as _urlencode
from bittrex.constants import BITTREX_GET_TRADE_HISTORY
from data_access.classes.PostRequestDetails import PostRequestDetails
from utils.key_utils import signed_string

from data_access.memory_cache import generate_nonce
from data_access.internet import send_post_request_with_header


def get_order_history_bittrex(key, pair_name):

    final_url = BITTREX_GET_TRADE_HISTORY + key.api_key + "&nonce=" + str(generate_nonce())

    if pair_name != "all":
        body = {"market": pair_name}
    else:
        body = {}

    final_url += _urlencode(body)

    headers = {"apisign": signed_string(final_url, key.secret)}

    post_details = PostRequestDetails(final_url, headers, body)

    err_msg = "get bittrex order history for time interval for pp={pp}".format(pp=post_details)

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body,
                                                    err_msg, max_tries=1)

    print "BITTREX", res

    return error_code, res
