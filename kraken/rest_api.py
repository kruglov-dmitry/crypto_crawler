from data_access.internet import send_post_request_with_header
from data_access.memory_cache import generate_nonce

from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level
from utils.file_utils import log_to_file
from utils.string_utils import float_to_str


from kraken.constants import KRAKEN_NUM_OF_DEAL_RETRY, KRAKEN_DEAL_TIMEOUT


def send_post_request_with_logging(post_details, err_msg):
    # FailFast motherfucker!
    res = send_post_request_with_header(post_details, err_msg, max_tries=KRAKEN_NUM_OF_DEAL_RETRY,
                                        timeout=KRAKEN_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res


def generate_body(pair_name, price, amount, order_type):
    return {
        "pair": pair_name,
        "type": order_type,
        "ordertype": "limit",
        "price": float_to_str(price),
        "volume": float_to_str(amount),
        "nonce": generate_nonce()
    }
