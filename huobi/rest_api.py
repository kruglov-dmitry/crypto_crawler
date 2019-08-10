from urllib import urlencode as _urlencode

from utils.key_utils import sign_string_256_base64
from utils.time_utils import ts_to_string_utc, get_now_seconds_utc
from utils.file_utils import log_to_file

from huobi.constants import HUOBI_DEAL_TIMEOUT, HUOBI_NUM_OF_DEAL_RETRY
from data_access.internet import send_post_request_with_header
from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, get_logging_level


def init_body(key):
    return [('AccessKeyId', key.api_key),
            ('SignatureMethod', 'HmacSHA256'),
            ('SignatureVersion', 2),
            ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]


def generate_url(key, base_url, path):
    body = [
        ('AccessKeyId', key.api_key),
        ('SignatureMethod', 'HmacSHA256'),
        ('SignatureVersion', 2),
        ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]

    message = _urlencode(body).encode('utf8')

    msg = "POST\n{base_url}\n{path}\n{msg1}".format(base_url=base_url, path=path, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    return _urlencode(body)


def generate_body_and_url_get_request(key, base_url, path):
    body = [
        ('AccessKeyId', key.api_key),
        ('SignatureMethod', 'HmacSHA256'),
        ('SignatureVersion', 2),
        ('Timestamp', ts_to_string_utc(get_now_seconds_utc(), '%Y-%m-%dT%H:%M:%S'))]

    message = _urlencode(body).encode('utf8')

    msg = "GET\n{base_url}\n{path}\n{msg1}".format(base_url=base_url, path=path, msg1=message)

    signature = sign_string_256_base64(key.secret, msg)

    body.append(("Signature", signature))

    return body, _urlencode(body)


def send_post_request_with_logging(post_details, err_msg):
    res = send_post_request_with_header(post_details, err_msg, max_tries=HUOBI_NUM_OF_DEAL_RETRY,
                                        timeout=HUOBI_DEAL_TIMEOUT)

    if get_logging_level() >= LOG_ALL_MARKET_RELATED_CRAP:
        print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)
        log_to_file(res, "market_utils.log")

    return res
