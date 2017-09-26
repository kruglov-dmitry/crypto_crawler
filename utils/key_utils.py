from constants import EXCHANGES

access_keys = {}


def load_keys(path):
    """
    :param path: full path to folder with public keys, each key should be named as corresponding exchange
    :return:
    """

    global access_keys

    for exchange in EXCHANGES:
        with open(path + "/" + exchange + ".key", 'r') as myfile:
            key = myfile.read()
            access_keys[exchange] = key


def get_key_by_exchange(exchange_id):
    global access_keys
    return access_keys.get(exchange_id)
