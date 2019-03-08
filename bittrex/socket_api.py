from requests import Session
from signalr import Connection

from zlib import decompress, MAX_WBITS
from json import loads
from base64 import b64decode
import time
import thread

from bittrex.currency_utils import get_currency_pair_to_bittrex, get_currency_pair_from_bittrex

from logging_tools.socket_logging import log_conect_to_websocket, log_error_on_receive_from_socket, \
    log_subscription_cancelled, log_websocket_disconnect, log_send_heart_beat_failed

from utils.file_utils import log_to_file
from debug_utils import SOCKET_ERRORS_LOG_FILE_NAME
from utils.time_utils import get_now_seconds_utc_ms, sleep_for
from services.sync_stage import set_stage

from enums.exchange import EXCHANGE
from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal
from data.OrderBook import OrderBook


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


def parse_socket_order_book_bittrex(order_book_snapshot, pair_id):
    """
    :param order_book_snapshot stringified json of following format:
        Bittrex order book format:
        "S" = "Sells"
        "Z" = "Buys"
        "M" = "MarketName"
        "f" = "Fills"
        "N" = "Nonce"

        For fills:
        "F" = "FillType": FILL | PARTIAL_FILL
        "I" = "Id"
        "Q" = "Quantity"
        "P" = "Price"
        "t" = "Total"
        "OT" = "OrderType": BUY | SELL
        "T" = "TimeStamp"

        {
            "S": [
                {
                    "Q": 4.29981987,
                    "R": 0.04083123
                },
                {
                    "Q": 0.59844883,
                    "R": 0.04083824
                }],
            "Z": [
                {
                    "Q": 10.8408461,
                    "R": 0.04069406
                },
                {
                    "Q": 0.9,
                    "R": 0.04069405
                }],
            "M": null,
            "f": [
                {
                    "F": "FILL",
                    "I": 274260522,
                    "Q": 0.37714445,
                    "P": 0.04083123,
                    "t": 0.01539927,
                    "OT": "BUY",
                    "T": 1535772645920
                },
                {
                    "F": "PARTIAL_FILL",
                    "I": 274260519,
                    "Q": 1.75676,
                    "P": 0.04069406,
                    "t": 0.07148969,
                    "OT": "SELL",
                    "T": 1535772645157
                }],
            "N": 28964
        }

    :return: newly assembled OrderBook object
    """

    timest_ms = get_now_seconds_utc_ms()

    sequence_id = long(order_book_snapshot["N"])

    sells = order_book_snapshot["S"]
    asks = []
    for new_sell in sells:
        asks.append(Deal(new_sell["R"], new_sell["Q"]))

    buys = order_book_snapshot["Z"]
    bids = []
    for new_buy in buys:
        bids.append(Deal(new_buy["R"], new_buy["Q"]))

    # DK WTF NOTE: ignore for now
    # fills = order_book_snapshot["f"]

    return OrderBook(pair_id, timest_ms, asks, bids, EXCHANGE.BITTREX, sequence_id)


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

        :param order_book_delta
        :return:
    """

    timest_ms = get_now_seconds_utc_ms()

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

    return OrderBookUpdate(sequence_id, bids, asks, timest_ms, trades_sell, trades_buy)


def get_order_book_bittrex_through_socket(pair_name, timest):
    """
        We run in separate thread polling of order book via socket api
        as soon as we got responce - return it from main thread.

    :param pair_name:
    :param timest:  ignored, for backword compatibility with other api method
    :return:

    """

    pair_id = get_currency_pair_from_bittrex(pair_name)

    bittrex_subscription = SubscriptionBittrex(pair_id, on_update=default_on_public)

    thread.start_new_thread(bittrex_subscription.request_order_book, ())

    while not bittrex_subscription.order_book_is_received:
        sleep_for(1)

    return bittrex_subscription.initial_order_book

#
#           Default methods to be used as callbacks
#


def process_message(message):
    deflated_msg = decompress(b64decode(message), -MAX_WBITS)
    return loads(deflated_msg.decode())


def default_on_receive(**kwargs):
    # FIXME NOTE: just ignore it!
    if 'R' in kwargs and type(kwargs['R']) is not bool:
        msg = process_message(kwargs['R'])
        print "Case 1", msg
    else:
        print kwargs


def default_on_error():
    print "Bittrex: default_on_error"


def default_on_public(exchange_id, args):
    print "Bittrex: default_on_public:"
    print exchange_id, args


class SubscriptionBittrex:
    def __init__(self, pair_id,
                 on_update=default_on_public,
                 base_url=BittrexParameters.URL,
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

        self.on_update = on_update

        self.hub = None

        self.order_book_is_received = False

        self.initial_order_book = None

        self.should_run = True

    def on_public(self, args):
        msg = process_message(args)
        log_to_file(msg, "bittrex.log")
        order_book_delta = parse_socket_update_bittrex(msg)

        if order_book_delta is None:
            err_msg = "Bittrex - cant parse update from message: {msg}".format(msg=msg)
            log_to_file(err_msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            self.on_update(EXCHANGE.BITTREX, order_book_delta)

    def on_receive(self, **kwargs):
        """
            heart beat and other stuff
        :param kwargs:
        :return:
        """

        if 'R' in kwargs and type(kwargs['R']) is not bool:
            msg = process_message(kwargs['R'])
            log_to_file(msg, "bittrex.log")
            if msg is not None:

                self.order_book_is_received = True
                self.initial_order_book = parse_socket_order_book_bittrex(msg, self.pair_id)

        else:
            try:
                msg = process_message(str(kwargs))
            except:
                msg = kwargs
            log_to_file(msg, "bittrex.log")
            if not self.order_book_is_received:
                time.sleep(5)

    def request_order_book(self):
        with Session() as session:
            connection = Connection(self.url, session)
            self.hub = connection.register_hub(self.hub_name)

            connection.received += self.on_receive

            connection.start()

            while self.order_book_is_received is not True:
                self.hub.server.invoke(BittrexParameters.QUERY_EXCHANGE_STATE, self.pair_name)
                connection.wait(5)  # otherwise it shoot thousands of query and we will be banned :(

            connection.close()

    def subscribe(self):
        self.should_run = True
        try:
            with Session() as session:
                self.connection = Connection(self.url, session)
                self.hub = self.connection.register_hub(self.hub_name)

                self.hub.client.on(BittrexParameters.MARKET_DELTA, self.on_public)

                self.connection.start()

                log_conect_to_websocket("Bittrex")

                while self.connection.started and self.should_run:
                    try:
                        self.hub.server.invoke(BittrexParameters.SUBSCRIBE_EXCHANGE_DELTA, self.pair_name)
                    except Exception as e:
                        log_send_heart_beat_failed("Bittrex", e)

                        set_stage(ORDER_BOOK_SYNC_STAGES.RESETTING)

                        # FIXME NOTE - still not sure - connection.wait(1)
                        self.should_run = False

                        break
                    sleep_for(1)
        except Exception as e:
            log_error_on_receive_from_socket("Bittrex", e)

            set_stage(ORDER_BOOK_SYNC_STAGES.RESETTING)

            self.should_run = False

        log_subscription_cancelled("Bittrex")

        self.disconnect()

    def disconnect(self):
        self.should_run = False

        sleep_for(3)  # To wait till all processing be ended

        try:
            self.connection.close()
        except Exception as e:
            log_websocket_disconnect("Bittrex", e)

    def is_running(self):
        return self.should_run
