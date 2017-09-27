from constants import EXCHANGES

access_keys = {}


class ExchangeKey(object):
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    @classmethod
    def from_file(cls, path, exchange):
        array = []
        with open(path + "/" + exchange + ".key", "r") as myfile:
            for line in myfile:
                array.append(line.rstrip())
                if len(array) == 2:
                    break

        return ExchangeKey(array[0], array[1])


def load_keys(path):
    """
    :param path: full path to folder with public keys, each key should be named as corresponding exchange
    :return:
    """

    global access_keys

    for exchange in EXCHANGES:
        key = ExchangeKey.from_file(path, exchange)
        access_keys[exchange] = key


def get_key_by_exchange(exchange_id):
    global access_keys
    return access_keys.get(exchange_id)
