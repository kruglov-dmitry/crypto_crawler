import time
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id
import hmac
import hashlib
from urllib import urlencode as _urlencode
import base64

access_keys = {}


class ExchangeKey(object):
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    @classmethod
    def from_file(cls, path, exchange_name):
        array = []
        with open(path + "/" + exchange_name.lower() + ".key", "r") as myfile:
            for line in myfile:
                array.append(line.rstrip())
                if len(array) == 2:
                    break

        return ExchangeKey(array[0], array[1])


def generate_nonce():
    # Additionally, all queries must include a "nonce" POST parameter.
    # The nonce parameter is an integer which must always be greater than the previous nonce used.
    # FIXME - store in db
    return int(round(time.time() * 1000))


def signed_body(body, secret):
    #  The query's POST data signed by your key's "secret" according to the HMAC-SHA512 method.
    payload = hmac.new(secret, _urlencode(body), hashlib.sha512).hexdigest()

    return payload


def signed_body_256(body, secret):
    #  The query's POST data signed by your key's "secret" according to the
    #  HMAC-SHA512 method.
    payload = hmac.new(secret.encode('utf-8'), _urlencode(body).encode('utf-8'), hashlib.sha256).hexdigest()

    return payload


def signed_string(body, secret):
    #  The query's POST data signed by your key's "secret" according to the HMAC-SHA512 method.
    payload = hmac.new(secret, body, hashlib.sha512).hexdigest()

    return payload


def sign_kraken(body, urlpath, secret):
    """ Sign request data according to Kraken's scheme.
    :param body: API request parameters
    :type body: dict
    :param urlpath: API URL path sans host
    :type urlpath: str
    :returns: signature digest
    """

    postdata = _urlencode(body)

    # Unicode-objects must be encoded before hashing
    encoded = (str(body['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    signature = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(signature.digest())

    return sigdigest.decode()


def load_keys(path):
    """
    :param path: full path to folder with public keys, each key should be named as corresponding exchange
    :return:
    """

    global access_keys

    for exchange_id in EXCHANGE.values():
        exchange_name = get_exchange_name_by_id(exchange_id)
        key = ExchangeKey.from_file(path, exchange_name)
        access_keys[exchange_id] = key


def get_key_by_exchange(exchange_id):
    global access_keys
    return access_keys.get(exchange_id)
