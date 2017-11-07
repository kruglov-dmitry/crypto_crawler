from constants import HTTP_TIMEOUT_SECONDS
import requests
import json
import hmac
import hashlib
from enums.status import STATUS
from utils.time_utils import sleep_for


def send_request(final_url, error_msg):
    res = STATUS.FAILURE, None
    try:
        responce = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS).json()
        res = STATUS.SUCCESS, responce
    except Exception, e:
        res = STATUS.FAILURE, error_msg + str(e)
        print error_msg, str(e)

    return res


def send_post_request_with_header(final_url, header, body, error_msg, max_tries):
    res = STATUS.FAILURE, None

    try_number = 0
    while try_number < max_tries:
        try:
            response = requests.post(final_url, data=body, headers=header, timeout=HTTP_TIMEOUT_SECONDS).json()

            # try to deal with problem - i.e. just wait an retry
            if "timeout" in response or "Service:Unavailable" in response:
                sleep_for(1)
                try_number += 1
            else:
                # NOTE: Consider it as success then, if not - extend possible checks above
                return STATUS.SUCCESS, response

            res = STATUS.FAILURE, response

        except Exception, e:
            res = STATUS.FAILURE, error_msg + str(e)
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
