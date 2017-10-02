from constants import HTTP_TIMEOUT_SECONDS
import requests
import json
import hmac
import hashlib


def send_request(final_url, error_msg):
    res = None
    try:
        res = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS).json()
    except Exception, e:
        print error_msg, str(e)

    return res


def send_post_request_with_header(final_url, header, body, error_msg):
    res = None
    try:
        res = requests.post(final_url, data=body, headers=header, timeout=HTTP_TIMEOUT_SECONDS).json()
    except Exception, e:
        print error_msg, str(e)

    return res


def send_post_request_signed(final_url, header, body, secret, nonce, error_msg):
    request = requests.Request('POST', final_url, params=body, headers=header)
    signature = hmac.new(secret, request.body, digestmod=hashlib.sha512)
    request.headers['Sign'] = signature.hexdigest()
    request.headers['nonce'] = nonce

    res = None
    with requests.Session() as session:
        res = session.send(request)

    # try:
    #     res = requests.post(final_url, data=json.dumps(body), headers=header, timeout=HTTP_TIMEOUT_SECONDS).json()
    # except Exception, e:
    #     print error_msg, str(e)

    return res
