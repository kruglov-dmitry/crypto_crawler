from constants import KRAKEN_BASE_API_URL, KRAKEN_BUY_ORDER, KRAKEN_NUM_OF_DEAL_RETRY, KRAKEN_DEAL_TIMEOUT

from debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.key_utils import sign_kraken
from utils.string_utils import float_to_str
from utils.file_utils import log_to_file

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce
from data_access.PostRequestDetails import PostRequestDetails

"""
from utils.time_utils import sleep_for
from enums.status import STATUS

implement idea of
place order at kraken no matter what, and on success can continue to play with other stuff

def add_buy_order_kraken_try_till_the_end(key, pair_name, price, amount):

    max_retry_num = 3
    retry_num = 0

    error_code, res = STATUS.FAILURE, None

    # prev_num_of_orders = order_state.get_total_num_of_orders()

    while retry_num < max_retry_num:
        retry_num += 1

        error_code, res = add_buy_order_kraken(key, pair_name, price, amount)

        if STATUS.FAILURE != error_code:
            return error_code, res

        # check whether we have added new deals
        # kraken may actually do it with some delay
        # lets try wait a bit to verify that they will not update it
        sleep_for(2)

        order_error_code, new_order_state = get_orders_kraken(key)

        if order_error_code == STATUS.SUCCESS:  # and prev_num_of_orders < new_order_state.get_total_num_of_orders():
            # FIXME well, ideally we have to look for pair_name, price and amount
            # But for now lets conclude that This crap did it!

            return STATUS.SUCCESS, res

        # otherwise - repeat
        sleep_for(1)

    return error_code, res
"""


def add_buy_order_kraken_url(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_BUY_ORDER

    current_nonce = generate_nonce()

    body = {
        "pair": pair_name,
        "type": "buy",
        "ordertype": "limit",
        "price": float_to_str(price),
        "volume": float_to_str(amount),
        "nonce": current_nonce
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_BUY_ORDER, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if should_print_debug():
        msg = "add_buy_order_kraken: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_buy_order_kraken(key, pair_name, price, amount):

    post_details = add_buy_order_kraken_url(key, pair_name, price, amount)

    err_msg = "add_buy_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name,
                                                                                                       amount=amount,
                                                                                                       price=price)

    # FailFast motherfucker!
    res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg,
                                        max_tries=KRAKEN_NUM_OF_DEAL_RETRY, timeout=KRAKEN_DEAL_TIMEOUT)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res