from constants import HTTP_TIMEOUT_SECONDS
import requests


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
        res = requests.post(final_url, data=json.dumps(body), headers=header, timeout=HTTP_TIMEOUT_SECONDS).json()
    except Exception, e:
        print error_msg, str(e)

    return res
