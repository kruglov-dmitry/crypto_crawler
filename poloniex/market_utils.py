from utils.key_utils import signed_body
from data_access.memory_cache import generate_nonce
from constants import POLONIEX_CANCEL_ORDER, POLONIEX_BUY_ORDER, POLONIEX_SELL_ORDER, POLONIEX_CHECK_BALANCE, \
    POLONIEX_GET_ORDER_HISTORY, POLONIEX_GET_OPEN_ORDERS
from data_access.internet import send_post_request_with_header
from debug_utils import should_print_debug
from data.Balance import Balance
from utils.time_utils import get_now_seconds_utc
from enums.status import STATUS
from data_access.PostRequestDetails import PostRequestDetails


def add_buy_order_poloniex(key, pair_name, price, amount):
    body = {
        "command": "buy",
        "currencyPair": pair_name,
        "rate": price,
        "amount": amount,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}
    # https://poloniex.com/tradingApi
    final_url = POLONIEX_BUY_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order poloniex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def add_sell_order_poloniex(key, pair_name, price, amount):
    body = {
        "command": "sell",
        "currencyPair": pair_name,
        "rate": price,
        "amount": amount,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_SELL_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order poloniex called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def cancel_order_poloniex(key, deal_id):
    body = {
        "command": "cancelOrder",
        "orderNumber" : deal_id,
        "nonce": generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CANCEL_ORDER

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel poloniex called for {deal_id}".format(deal_id=deal_id)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if should_print_debug():
        print res

    return res


def get_balance_poloniex_post_details(key):
    body = {
        'command': 'returnCompleteBalances',
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CHECK_BALANCE

    res = PostRequestDetails(final_url, headers, body)

    # if should_print_debug():
    #    print res

    return res


def get_balance_poloniex_result_processor(json_document, timest):
    if json_document is not None:
        return Balance.from_poloniex(timest, json_document)

    return None


def get_balance_poloniex(key):
    """
    https://poloniex.com/tradingApi
    {'Key': 'QN6SDFQG-XVG2CGG3-WDDG2WDV-VXZ7MYL3',
    'Sign': '368a800fcd4bc0f0d95151ed29c9f84ddf6cae6bc366d3105db1560318da72aa82281b5ea52f4d4ec929dd0eabc7339fe0e7dc824bf0f1c64e099344cd6e74d0'}
    {'nonce': 1508507033330, 'command': 'returnCompleteBalances'}

    {"LTC":{"available":"5.015","onOrders":"1.0025","btcValue":"0.078"},"NXT:{...} ... }

    """

    post_details = get_balance_poloniex_post_details(key)

    err_msg = "check poloniex balance called"

    timest = get_now_seconds_utc()
    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=3)

    if error_code == STATUS.SUCCESS:
        res = Balance.from_poloniex(timest, res)

    return error_code, res


def get_order_history_poloniex_post_details(key, currency_name):
    body = {
        'command': 'returnTradeHistory',
        'currencyPair': currency_name,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_ORDER_HISTORY

    res = PostRequestDetails(final_url, headers, body)

    # if should_print_debug():
    #    print res

    return res


def get_orders_history_poloniex(key, currency_name):
    post_details = get_order_history_poloniex_post_details(key, currency_name)

    err_msg = "get poloniex order history"
    print err_msg

    timest = get_now_seconds_utc()
    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=3)

    return error_code, res


def get_open_order_poloniex_post_details(key, currency_name):
    body = {
        'command': 'returnOpenOrders',
        'currencyPair': currency_name,
        'nonce': generate_nonce()
    }
    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_GET_OPEN_ORDERS

    res = PostRequestDetails(final_url, headers, body)

    # if should_print_debug():
    #    print res

    return res


def get_open_orders_poloniex(key, currency_name):
    post_details = get_open_order_poloniex_post_details(key, currency_name)

    err_msg = "get poloniex open orders"
    print err_msg

    error_code, res = send_post_request_with_header(post_details.final_url, post_details.headers, post_details.body, err_msg, max_tries=3)

    return error_code, res