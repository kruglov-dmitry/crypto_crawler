from utils.key_utils import generate_nonce, signed_body
from constants import POLONIEX_CANCEL_ORDER, POLONIEX_BUY_ORDER, POLONIEX_SELL_ORDER, POLONIEX_CHECK_BALANCE
from data_access.internet import send_post_request_with_header
from debug_utils import should_print_debug
from data.Balance import Balance
from utils.time_utils import get_now_seconds
from enums.status import STATUS


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


def get_balance_poloniex(key):
    """
    https://poloniex.com/tradingApi
    {'Key': 'QN6SDFQG-XVG2CGG3-WDDG2WDV-VXZ7MYL3',
    'Sign': '368a800fcd4bc0f0d95151ed29c9f84ddf6cae6bc366d3105db1560318da72aa82281b5ea52f4d4ec929dd0eabc7339fe0e7dc824bf0f1c64e099344cd6e74d0'}
    {'nonce': 1508507033330, 'command': 'returnBalances'}

    {u'XVC': u'0.00000000', u'SRCC': u'0.00000000', u'EXE': u'0.00000000', u'WC': u'0.00000000', u'MIL': u'0.00000000',
                                                        ....
     u'UNITY': u'0.00000000', u'XST': u'0.00000000', u'EBT': u'0.00000000', u'ARDR': u'26712.05233871', u'eTOK': u'0.00000000',
     u'SDC': u'0.00000000', u'NRS': u'0.00000000', u'TRUST': u'0.00000000', u'POT': u'0.00000000', u'PIGGY': u'0.00000000'}

    """

    body = {
        'command': 'returnBalances',
        'nonce': generate_nonce()
    }

    headers = {"Key": key.api_key, "Sign": signed_body(body, key.secret)}

    # https://poloniex.com/tradingApi
    final_url = POLONIEX_CHECK_BALANCE

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check poloniex balance called"

    timest = get_now_seconds()
    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=3)

    if res[0] == STATUS.SUCCESS:
        res = STATUS.SUCCESS, Balance.from_poloniex(timest, res[1])

    return res
