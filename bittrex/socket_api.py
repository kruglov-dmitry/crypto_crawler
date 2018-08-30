from requests import Session
from signalr import Connection

from zlib import decompress, MAX_WBITS
from json import loads
from base64 import b64decode

from bittrex.currency_utils import get_currency_pair_to_bittrex

from utils.file_utils import log_to_file
from debug_utils import SOCKET_ERRORS_LOG_FILE_NAME
from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE
from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal


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

    BITTREX_ORDER_ADD = 0
    BITTREX_ORDER_REMOVE = 1
    BITTREX_ORDER_UPDATE = 2


def parse_socket_update_bittrex(order_book_delta):
    """
        https://bittrex.github.io/#callback-for-1

        "S" = "Sells"
        "Z" = "Buys"

        "Q" = "Quantity"
        "R" = "Rate"
        "TY" = "Type"
        The Type key can be one of the following values: 0 = ADD, 1 = REMOVE, 2 = UPDATE

        "M" = "MarketName"
        "N" = "Nonce"

        "f" = "Fills"

        3 {u'S': [],
            u'Z': [{u'Q': 0.0, u'R': 0.04040231, u'TY': 1}, {u'Q': 0.78946119, u'R': 0.00126352, u'TY': 0}],
            u'M': u'BTC-DASH',
            u'f': [],
            u'N': 15692}

        3 {u'S': [],
            u'Z': [{u'Q': 1.59914865, u'R': 0.040436, u'TY': 0}, {u'Q': 0.0, u'R': 0.04040232, u'TY': 1}],
            u'M': u'BTC-DASH',
            u'f': [],
            u'N': 15691}


        u'f': [
            {u'Q': 0.11299437,
                u'R': 0.042135,
                u'OT': u'BUY',
                u'T': 1527961548500},
                {u'Q': 0.39487459, u'R': 0.04213499, u'OT': u'BUY', u'T': 1527961548500}],

        :param order_book_delta:
        :return:
    """

    sequence_id = long(order_book_delta["N"])

    asks = []
    bids = []
    trades_sell = []
    trades_buy = []

    sells = order_book_delta["S"]
    buys = order_book_delta["Z"]
    fills = order_book_delta["f"]

    for new_sell in sells:

        new_deal = Deal(new_sell["R"], new_sell["Q"])

        if "TY" not in new_sell:
            msg = "Bittrex socket update - within SELL array some weird format - no TY - {wtf}".format(
                wtf=new_sell)
            log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            continue

        type_update = int(new_sell["TY"])

        if type_update in [BittrexParameters.BITTREX_ORDER_ADD, BittrexParameters.BITTREX_ORDER_UPDATE]:
            asks.append(new_deal)
        elif type_update == BittrexParameters.BITTREX_ORDER_REMOVE:
            asks.append(Deal(new_sell["R"], 0))
        else:
            msg = "Bittrex socket un-supported sells format? {wtf}".format(wtf=new_sell)
            log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    for new_buy in buys:

        new_deal = Deal(new_buy["R"], new_buy["Q"])

        if "TY" not in new_buy:
            msg = "Bittrex socket update - within BUYS array some weird format - no TY - {wtf}".format(wtf=new_buy)
            log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            continue

        type_update = int(new_buy["TY"])

        if type_update in [BittrexParameters.BITTREX_ORDER_ADD, BittrexParameters.BITTREX_ORDER_UPDATE]:
            bids.append(new_deal)
        elif type_update == BittrexParameters.BITTREX_ORDER_REMOVE:
            bids.append(Deal(new_buy["R"], 0))
        else:
            msg = "Bittrex socket un-supported buys format? {wtf}".format(wtf=new_buy)
            log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    for new_fill in fills:
        new_deal = Deal(new_fill["R"], new_fill["Q"])

        if "TY" in new_fill:
            msg = "Bittrex socket update - within FILLS array some weird format - no TY - {wtf}".format(wtf=new_fill)
            log_to_file(msg, "should_not_see_you.log")
            continue

        deal_direction = DEAL_TYPE.BUY if "BUY" in new_fill["OT"] else DEAL_TYPE.SELL

        if deal_direction == DEAL_TYPE.BUY:
            trades_buy.append(new_deal)
        else:
            trades_sell.append(new_deal)

    return OrderBookUpdate(sequence_id, bids, asks, trades_sell, trades_buy)

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

    # print kwargs
    pass


def default_on_public(exchange_id, args, updates_queue):
    msg = process_message(args)
    print exchange_id, msg, updates_queue


class SubscriptionBittrex:
    def __init__(self, pair_id, on_update=default_on_public, base_url=BittrexParameters.URL,
                 hub_name=BittrexParameters.HUB, updates_queue=None):
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

        self.on_update = on_update
        self.updates_queue = updates_queue

        self.hub = None

    def on_error(self, error):
        print "Error:", error
        self.subscribe()

    def on_update(self, args):
        msg = process_message(args)
        self.on_update(EXCHANGE.BITTREX, msg, self.updates_queue)

    def subscribe(self):
        with Session() as session:
            connection = Connection(self.url, session)
            self.hub = connection.register_hub(self.hub_name)

            self.hub.client.on(BittrexParameters.MARKET_DELTA, self.on_update)

            connection.error += self.on_error

            connection.start()

            while connection.started:
                self.hub.server.invoke(BittrexParameters.SUBSCRIBE_EXCHANGE_DELTA, self.pair_name)

