from json import loads
import websocket
from websocket import create_connection

from binance.currency_utils import get_currency_pair_to_binance
from enums.exchange import EXCHANGE
from data.order_book_update import OrderBookUpdate
from data.deal import Deal

from utils.debug_utils import get_logging_level, LOG_ALL_TRACE, SOCKET_ERRORS_LOG_FILE_NAME
from utils.file_utils import log_to_file
from utils.system_utils import die_hard
from utils.time_utils import get_now_seconds_utc_ms

from logging_tools.socket_logging import log_conect_to_websocket, log_error_on_receive_from_socket, \
    log_subscription_cancelled, log_websocket_disconnect


def parse_socket_update_binance(order_book_delta):
    """
        How to manage a local order book correctly
        Open a stream to wss://stream.binance.com:9443/ws/bnbbtc@depth
        Buffer the events you receive from the stream
        Get a depth snapshot from **https://www.binance.com/api/v1/depth?symbol=BNBBTC&limit=1000"
        Drop any event where u is <= lastUpdateId in the snapshot
        The first processed should have U <= lastUpdateId+1 AND u >= lastUpdateId+1
        While listening to the stream, each new event's U should be equal to the previous event's u+1
        The data in each event is the absolute quantity for a price level
        If the quantity is 0, remove the price level
        Receiving an event that removes a price level that is not in your local order book can happen and is normal.

        4

        "U": 157,           // First update ID in event
        "u": 160,           // Final update ID in event

        {"e": "depthUpdate", "E": 1527861613915, "s": "DASHBTC", "U": 45790140, "u": 45790142,
        "b": [["0.04073500", "2.02000000", []], ["0.04073200", "0.00000000", []]],
        "a": [["0.04085300", "0.00000000", []]]}

        :param order_book_delta:
        :return:
    """

    timest_ms = get_now_seconds_utc_ms()

    sequence_id = long(order_book_delta["U"])
    sequence_id_end = long(order_book_delta["u"])

    asks = []
    bids = []
    trades_sell = []
    trades_buy = []

    for a in order_book_delta["a"]:
        asks.append(Deal(a[0], a[1]))

    for a in order_book_delta["b"]:
        bids.append(Deal(a[0], a[1]))

    return OrderBookUpdate(sequence_id, bids, asks, timest_ms, trades_sell, trades_buy, sequence_id_end)


def process_message(compress_data):
    return loads(compress_data)


class BinanceParameters:
    URL = "wss://stream.binance.com:9443/ws/"

    SUBSCRIBE_UPDATE = "{pair_name}@depth"


def default_on_error():
    print "Binance: default_on_error"


def default_on_public(exchange_id, args):
    print "Binance: odefault_on_public:"
    print exchange_id, args


class SubscriptionBinance:
    def __init__(self, pair_id, on_update=default_on_public, base_url=BinanceParameters.URL):
        """
        :param pair_id:         - currency pair to be used for trading
        :param on_update:       - idea is the following:
                                    we pass reference to method WITH initialized order book for that pair_id
                                    whenever we receive update we update order book and trigger checks for arbitrage
        :param base_url:        - web-socket subscription end points
        """

        self.url = base_url

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_binance(self.pair_id).lower()

        self.subscription_url = BinanceParameters.URL + BinanceParameters.SUBSCRIBE_UPDATE.format(pair_name=self.pair_name)

        self.on_update = on_update

        self.should_run = False

    def on_public(self, ws, args):
        msg = process_message(args)
        order_book_delta = parse_socket_update_binance(msg)

        if order_book_delta is None:
            err_msg = "Binance - cant parse update from message: {msg}".format(msg=msg)
            log_to_file(err_msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            self.on_update(EXCHANGE.BINANCE, order_book_delta)

    def subscribe(self):

        #
        #       FIXME DBG PART - REMOVE AFTER TESTS
        #

        if self.should_run:
            die_hard("Binance another running?")

        msg = "Binance - call subscribe!"
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
        print msg

        self.should_run = True

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        # Create connection
        try:
            self.ws = create_connection(self.subscription_url, enable_multithread=True)
            self.ws.settimeout(15)
        except Exception as e:
            print('Binance - connect ws error - {}, retry...'.format(str(e)))

            self.disconnect()

            return

        # actual subscription - for binance can be embedded within url
        # self.ws.send(self.subscription_url)

        log_conect_to_websocket("Binance")

        # event loop
        while self.should_run:
            try:
                compressed_data = self.ws.recv()
                self.on_public(self.ws, compressed_data)
            except Exception as e:

                log_error_on_receive_from_socket("Binance", e)

                break

        log_subscription_cancelled("Binance")

        self.disconnect()

    def disconnect(self):
        self.should_run = False

        try:
            self.ws.close()
        except Exception as e:
            log_websocket_disconnect("Binance", e)

    def is_running(self):
        return self.should_run
