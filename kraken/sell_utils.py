from kraken.constants import KRAKEN_BASE_API_URL, KRAKEN_SELL_ORDER, KRAKEN_NUM_OF_DEAL_RETRY, KRAKEN_DEAL_TIMEOUT

from data_access.classes.PostRequestDetails import PostRequestDetails
from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level

from utils.file_utils import log_to_file
from utils.key_utils import sign_kraken
from utils.string_utils import float_to_str


def add_sell_order_kraken_url(key, pair_name, price, amount):
    # https://api.kraken.com/0/private/AddOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_SELL_ORDER

    current_nonce = generate_nonce()

    body = {
        "pair": pair_name,
        "type": "sell",
        "ordertype": "limit",
        "price": float_to_str(price),
        "volume": float_to_str(amount),
        "nonce": current_nonce
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_SELL_ORDER, key.secret)}

    res = PostRequestDetails(final_url, headers, body)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        msg = "add_sell_order_kraken_url: {res}".format(res=res)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(msg, "market_utils.log")

    return res


def add_sell_order_kraken(key, pair_name, price, amount):

    posr_details = add_sell_order_kraken_url(key, pair_name, price, amount)

    err_msg = "add_sell_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name,
                                                                                                        amount=amount,
                                                                                                        price=price)

    res = send_post_request_with_header(posr_details, err_msg,
                                        max_tries=KRAKEN_NUM_OF_DEAL_RETRY, timeout=KRAKEN_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
