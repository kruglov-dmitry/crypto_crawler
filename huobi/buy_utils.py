import json
from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_BUY_ORDER, HUOBI_NUM_OF_DEAL_RETRY, HUOBI_DEAL_TIMEOUT, HUOBI_API_URL, HUOBI_API_ONLY
from huobi.account_utils import get_huobi_account

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_post_request_with_header

from debug_utils import get_logging_level, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from utils.file_utils import log_to_file
from utils.key_utils import sign_string_256_base64
from utils.string_utils import float_to_str
from utils.time_utils import ts_to_string_utc, get_now_seconds_utc


def add_buy_order_huobi_url(key, pair_name, price, amount):

    final_url = HUOBI_API_URL + HUOBI_BUY_ORDER + "?"

    body = [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]

    message = _urlencode(body).encode('utf8')

    msg = "POST\n{base_url}\n{path}\n{msg1}".format(base_url=HUOBI_API_ONLY, path=HUOBI_BUY_ORDER, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    final_url += _urlencode(body)

    params = json.dumps({
        "account-id": get_huobi_account(key),
        "amount": float_to_str(amount),
        "price": float_to_str(price),
        "source": "api",
        "symbol": pair_name,
        "type": "buy-limit"
    })

    headers = {'content-type': 'application/json', 'accept': 'application/json'}

    res = PostRequestDetails(final_url, headers, params)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_buy_order_huobi: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_buy_order_huobi(key, pair_name, price, amount):

    post_details = add_buy_order_huobi_url(key, pair_name, price, amount)

    err_msg = "add_buy_order_huobi  called for {pair} for amount = {amount} with price {price}".format(
        pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(post_details, err_msg, max_tries=HUOBI_NUM_OF_DEAL_RETRY,
                                        timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
