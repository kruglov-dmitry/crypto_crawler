from kraken.constants import KRAKEN_BASE_API_URL, KRAKEN_BUY_ORDER
from kraken.rest_api import send_post_request_with_logging, generate_body

from data_access.classes.post_request_details import PostRequestDetails

from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

from utils.file_utils import log_to_file
from utils.key_utils import sign_kraken


def add_buy_order_kraken_url(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_BUY_ORDER

    body = generate_body(pair_name, price, amount, "buy")

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_BUY_ORDER, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_buy_order_kraken: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_buy_order_kraken(key, pair_name, price, amount):

    post_details = add_buy_order_kraken_url(key, pair_name, price, amount)

    err_msg = "add_buy_order kraken called for {pair} for amount = {amount} with price {price}".format(
        pair=pair_name, amount=amount, price=price)

    return send_post_request_with_logging(post_details, err_msg)
