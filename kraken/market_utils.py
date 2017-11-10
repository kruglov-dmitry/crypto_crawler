from constants import KRAKEN_BASE_API_URL, KRAKEN_CANCEL_ORDER, KRAKEN_BUY_ORDER, KRAKEN_SELL_ORDER, KRAKEN_CHECK_BALANCE
from data_access.internet import send_post_request_with_header
from debug_utils import should_print_debug
from utils.key_utils import generate_nonce, sign_kraken
from data.Balance import Balance
from utils.time_utils import get_now_seconds
from enums.status import STATUS


def float_to_str(f):
    float_string = repr(f)
    if 'e' in float_string:  # detect scientific notation
        digits, exp = float_string.split('e')
        digits = digits.replace('.', '').replace('-', '')
        exp = int(exp)
        zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = '-' if f < 0 else ''
        if exp > 0:
            float_string = '{}{}{}.0'.format(sign, digits, zero_padding)
        else:
            float_string = '{}0.{}{}'.format(sign, zero_padding, digits)
    return float_string


def add_buy_order_kraken(key, pair_name, price, amount):
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

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_buy_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if should_print_debug():
        print res

    return res


def add_sell_order_kraken(key, pair_name, price, amount):
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

    if should_print_debug():
        print final_url, headers, body

    err_msg = "add_sell_order kraken called for {pair} for amount = {amount} with price {price}".format(pair=pair_name, amount=amount, price=price)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if should_print_debug():
        print res

    return res


def cancel_order_kraken(key, deal_id):
    # https://api.kraken.com/0/private/CancelOrder
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CANCEL_ORDER

    body = {
        "txid": deal_id,
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CANCEL_ORDER, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "cancel kraken called for {deal_id}".format(deal_id=deal_id)

    res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if should_print_debug():
        print res

    return res


def get_balance_kraken(key):
    """
    Example of request \ responce
        https://api.kraken.com/0/private/Balance
        {'API-Key': 'whatever',
         'API-Sign': u'whatever'}
        {'nonce': 1508503223939}

    Responce:
    {u'result': {u'DASH': u'33.2402410500', u'BCH': u'22.4980093900', u'ZUSD': u'12747.4370', u'XXBT': u'3.1387700870',
                 u'EOS': u'2450.8822990100', u'USDT': u'77.99709699', u'XXRP': u'0.24804100',
                 u'XREP': u'349.7839715600', u'XETC': u'508.0140331400', u'XETH': u'88.6104554900'}, u'error': []}
    """
    final_url = KRAKEN_BASE_API_URL + KRAKEN_CHECK_BALANCE

    body = {
        "nonce": generate_nonce()
    }

    headers = {"API-Key": key.api_key, "API-Sign": sign_kraken(body, KRAKEN_CHECK_BALANCE, key.secret)}

    if should_print_debug():
        print final_url, headers, body

    err_msg = "check kraken balance called"

    timest = get_now_seconds()
    error_code, res = send_post_request_with_header(final_url, headers, body, err_msg, max_tries=5)

    if error_code == STATUS.SUCCESS and "result" in res:
        res = Balance.from_kraken(timest, res["result"])

    return error_code, res

