from requests import Session
from signalr import Connection

from zlib import decompress, MAX_WBITS
from json import loads
from base64 import b64decode

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
    # FIXME NOTE: just ignore it!
    # if 'R' in kwargs and type(kwargs['R']) is not bool:
    #    msg = process_message(kwargs['R'])

    pass


def default_on_public(exchange_id, args):
    msg = process_message(args)
    print exchange_id, msg


class SubscriptionBittrex:
    def __init__(self, pair_id, on_update=default_on_public, base_url=BittrexParameters.URL,
                 hub_name=BittrexParameters.HUB):
        """
        :param pair_id:     - currency pair to be used for trading
        :param base_url:    - web-socket subscription end points
        :param hub_name:    - Bittrex-specific url for market update
        :param on_update:   - idea is the following:
            we pass reference to method WITH initialized order book for that pair_id
            whenever we receive update we update order book and trigger checks for arbitrage
        """

        self.url = base_url
        self.hub_name = hub_name

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_bittrex(self.pair_id)

        # self.on_receive = on_receive

        self.on_update = on_update

        self.hub = None

    def on_error(self, error):
        print "Error:", error
        self.subscribe()

    def on_update(self, args):
        msg = process_message(args)
        self.on_update(EXCHANGE.BITTREX, msg)

    def subscribe(self):
        with Session() as session:
            connection = Connection(self.url, session)
            self.hub = connection.register_hub(self.hub_name)

            # connection.received += self.on_receive

            self.hub.client.on(BittrexParameters.MARKET_DELTA, self.on_update)

            connection.error += self.on_error

            connection.start()

            self.hub.server.invoke(BittrexParameters.QUERY_EXCHANGE_STATE, self.pair_name)
            # connection.wait(10)

            # with connection:
            while connection.started:
                self.hub.server.invoke(BittrexParameters.SUBSCRIBE_EXCHANGE_DELTA, self.pair_name)
