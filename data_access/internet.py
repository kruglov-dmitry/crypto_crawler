from constants import HTTP_TIMEOUT_SECONDS
import requests


def send_request(final_url, error_msg):
    res = None
    try:
        res = requests.get(final_url, timeout=HTTP_TIMEOUT_SECONDS).json()
    except Exception, e:
        print error_msg, str(e)

    return res