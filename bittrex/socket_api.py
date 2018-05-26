from requests import Session
from signalr import Connection

from zlib import decompress, MAX_WBITS
from json import loads
from base64 import b64decode

import hashlib
import hmac

from bittrex.currency_utils import get_currency_pair_to_bittrex

from enums.exchange import EXCHANGE


class BittrexParameters:
    # Connection parameters
    URL = 'https://socket.bittrex.com/signalr'
    HUB = 'c2'

    # Endpoints for Callbacks
    MARKET_DELTA = 'uE'
    SUMMARY_DELTA = 'uS'
    SUMMARY_DELTA_LITE = 'uL'
    BALANCE_DELTA = 'uB'
    ORDER_DELTA = 'uO'

    #
    QUERY_EXCHANGE_STATE = "QueryExchangeState"
    SUBSCRIBE_EXCHANGE_DELTA = "SubscribeToExchangeDeltas"


#
#           Default methods to be used as callbacks
#

def process_message(message):
    deflated_msg = decompress(b64decode(message), -MAX_WBITS)
    return loads(deflated_msg.decode())


def default_on_receive(**kwargs):
    # print "on_receive", kwargs
    if 'R' in kwargs and type(kwargs['R']) is not bool:
        msg = process_message(kwargs['R'])
        # print msg


def default_on_public(args):
    # print "on_public", args
    msg = process_message(args)
    # print msg


def default_on_private(args):
    print "on_private", args


# create error handler
def default_on_error(error):
    print('error: ', error)


class SubscriptionBittrex:
    def __init__(self, pair_id, on_update=default_on_public, base_url=BittrexParameters.URL,
                 hub_name=BittrexParameters.HUB, on_receive=default_on_receive, on_error=default_on_error):
        """
        :param pair_id:     - currency pair to be used for trading
        :param base_url:    - web-socket subscription end points
        :param hub_name:    - Bittrex-specific url for market update
        :param on_receive:  - pass
        :param on_error:    - recconect
        :param on_update:   - idea is the following:
            we pass reference to method WITH initialized order book for that pair_id
            whenever we receive update we update order book and trigger checks for arbitrage
        """

        self.url = base_url
        self.hub_name = hub_name

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_bittrex(self.pair_id)

        self.on_receive = on_receive
        self.on_error = on_error
        self.on_update = on_update

        self.hub = None

    def on_public(self, args):
        print "on_public", args
        msg = process_message(args)
        self.on_update(EXCHANGE.BITTREX, msg)

    def subscribe(self):
        with Session() as session:
            connection = Connection(self.url, session)
            self.hub = connection.register_hub(self.hub_name)

            connection.received += self.on_receive

            self.hub.client.on(BittrexParameters.MARKET_DELTA, self.on_public)

            connection.error += default_on_error

            connection.start()

            self.hub.server.invoke(BittrexParameters.QUERY_EXCHANGE_STATE, self.pair_name)
            connection.wait(10)

            # with connection:
            while connection.started:
                self.hub.server.invoke(BittrexParameters.SUBSCRIBE_EXCHANGE_DELTA, self.pair_name)


#
#           Not used for now
#

def create_signature(api_secret, challenge):
    api_sign = hmac.new(api_secret.encode(), challenge.encode(), hashlib.sha512).hexdigest()
    return api_sign


def main():
    with Session() as session:
        connection = Connection("https://socket.bittrex.com/signalr", session)
        hub = connection.register_hub('c2')

        connection.received += default_on_receive

        hub.client.on(BittrexParameters.MARKET_DELTA, default_on_public)
        hub.client.on(BittrexParameters.SUMMARY_DELTA, default_on_public)
        hub.client.on(BittrexParameters.SUMMARY_DELTA_LITE, default_on_public)
        hub.client.on(BittrexParameters.BALANCE_DELTA, default_on_private)
        hub.client.on(BittrexParameters.ORDER_DELTA, default_on_private)

        connection.error += default_on_error

        connection.start()

        hub.server.invoke("QueryExchangeState", "BTC-ETH")
        connection.wait(10)

        # with connection:
        while connection.started:
            hub.server.invoke("SubscribeToExchangeDeltas", "BTC-ETH")


if __name__ == "__main__":
    main()
