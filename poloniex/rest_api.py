from poloniex.constants import POLONIEX_NUM_OF_DEAL_RETRY, POLONIEX_DEAL_TIMEOUT

from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from utils.string_utils import float_to_str
from utils.file_utils import log_to_file

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level


def generate_body(pair_name, price, amount, order_type):
    return {
        "command": order_type,
        "currencyPair": pair_name,
        "rate": float_to_str(price),
        "amount": float_to_str(amount),
        "nonce": generate_nonce()
    }


def send_post_request_with_logging(post_details, err_msg):
    res = send_post_request_with_header(post_details, err_msg, max_tries=POLONIEX_NUM_OF_DEAL_RETRY,
                                        timeout=POLONIEX_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
