from requests import Session
from signalr import Connection

from zlib import decompress, MAX_WBITS
from json import loads
from base64 import b64decode

import hashlib
import hmac


class Constant:
    pass


class BittrexParameters(Constant):
    # Connection parameters
    URL = 'https://socket.bittrex.com/signalr'
    HUB = 'c2'
    # Callbacks
    MARKET_DELTA = 'uE'
    SUMMARY_DELTA = 'uS'
    SUMMARY_DELTA_LITE = 'uL'
    BALANCE_DELTA = 'uB'
    ORDER_DELTA = 'uO'


def process_message(message):
    deflated_msg = decompress(b64decode(message), -MAX_WBITS)
    return loads(deflated_msg.decode())


def create_signature(api_secret, challenge):
    api_sign = hmac.new(api_secret.encode(), challenge.encode(), hashlib.sha512).hexdigest()
    return api_sign


def on_receive(**kwargs):
    print "on_receive", kwargs
    if 'R' in kwargs and type(kwargs['R']) is not bool:
        msg = process_message(kwargs['R'])
        if msg is not None:
            print msg


def on_public(args):
    print "on_public", args
    msg = process_message(args)
    if msg is not None:
        print msg


def on_private(args):
    # print 100
    pass


# create error handler
def print_error(error):
    print('error: ', error)


def main():
    with Session() as session:
        connection = Connection("https://socket.bittrex.com/signalr", session)
        hub = connection.register_hub('c2')

        connection.received += on_receive

        hub.client.on(BittrexParameters.MARKET_DELTA, on_public)
        hub.client.on(BittrexParameters.SUMMARY_DELTA, on_public)
        hub.client.on(BittrexParameters.SUMMARY_DELTA_LITE, on_public)
        hub.client.on(BittrexParameters.BALANCE_DELTA, on_private)
        hub.client.on(BittrexParameters.ORDER_DELTA, on_private)

        connection.error += print_error

        connection.start()

        hub.server.invoke("QueryExchangeState", "BTC-ETH")
        connection.wait(10)

        # with connection:
        while connection.started:
            hub.server.invoke("SubscribeToExchangeDeltas", "BTC-ETH")


if __name__ == "__main__":
    main()
