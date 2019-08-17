from huobi.constants import HUOBI_CHECK_BALANCE, HUOBI_DEAL_TIMEOUT, HUOBI_API_URL, \
    HUOBI_API_ONLY, HUOBI_GET_HEADERS
from huobi.error_handling import is_error
from huobi.account_utils import get_huobi_account

from data.balance import Balance

from data_access.classes.post_request_details import PostRequestDetails
from data_access.internet import send_get_request_with_header

from utils.debug_utils import print_to_console, LOG_ALL_MARKET_NETWORK_RELATED_CRAP, ERROR_LOG_FILE_NAME, \
    should_print_debug, get_logging_level, LOG_ALL_DEBUG

from enums.status import STATUS

from utils.time_utils import get_now_seconds_utc
from utils.file_utils import log_to_file
from huobi.rest_api import generate_body_and_url_get_request


def get_balance_huobi_post_details(key):
    path = HUOBI_CHECK_BALANCE + get_huobi_account(key) + "/balance"
    final_url = HUOBI_API_URL + path + "?"

    body, url = generate_body_and_url_get_request(key, HUOBI_API_ONLY, path)
    final_url += url

    res = PostRequestDetails(final_url, HUOBI_GET_HEADERS, body)

    if should_print_debug():
        print_to_console(res, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)

    return res


def get_balance_huobi_result_processor(json_document, timest):
    if not is_error(json_document) and "data" in json_document and json_document["data"]:
        return STATUS.SUCCESS, Balance.from_huobi(timest, json_document["data"])

    msg = "get_balance_huobi_result_processor - error response - {er}".format(er=json_document)
    log_to_file(msg, ERROR_LOG_FILE_NAME)

    return STATUS.FAILURE, None


def get_balance_huobi(key):

    post_details = get_balance_huobi_post_details(key)

    err_msg = "check huobi balance called"

    timest = get_now_seconds_utc()

    status_code, res = send_get_request_with_header(
        post_details.final_url, post_details.headers, err_msg,
        timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_DEBUG:
        log_to_file(res, "balance.log")

    if status_code == STATUS.SUCCESS:
        status_code, res = get_balance_huobi_result_processor(res, timest)

    return status_code, res
