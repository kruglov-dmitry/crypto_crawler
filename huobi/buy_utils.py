from urllib import urlencode as _urlencode

from huobi.constants import HUOBI_BUY_ORDER, HUOBI_NUM_OF_DEAL_RETRY, HUOBI_DEAL_TIMEOUT
from huobi.market_utils import get_huobi_account

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header

from debug_utils import get_logging_level, print_to_console, LOG_ALL_MARKET_RELATED_CRAP

from utils.file_utils import log_to_file
from utils.key_utils import signed_body_256
from utils.string_utils import float_to_str


def add_buy_order_huobi_url(key, pair_name, price, amount):

    final_url = HUOBI_BUY_ORDER

    body = {
        "account-id": get_huobi_account(),
        "amount": amount,
        "price": float_to_str(price),
        "source": "api",
        "symbol": pair_name,
        "type": "buy-limit"
    }

    signature = signed_body_256(body, key.secret)

    body["signature"] = signature

    final_url += _urlencode(body)

    headers = {"X-MBX-APIKEY": key.api_key}

    # Yeah, body after that should be empty
    body = {}

    res = PostRequestDetails(final_url, headers, body)

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