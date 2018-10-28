from json import loads
import websocket
import ssl
from websocket import create_connection

from binance.currency_utils import get_currency_pair_to_binance
from enums.exchange import EXCHANGE
from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal

from utils.time_utils import get_now_seconds_utc_ms, sleep_for
from debug_utils import get_logging_level, LOG_ALL_TRACE, SOCKET_ERRORS_LOG_FILE_NAME
from utils.system_utils import die_hard
from utils.file_utils import log_to_file

from enums.sync_stages import ORDER_BOOK_SYNC_STAGES


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


def process_message(compressData):
    return loads(compressData)


class BinanceParameters:
    URL = "wss://stream.binance.com:9443/ws/"

    SUBSCRIBE_UPDATE = "{pair_name}@depth"


def default_on_error():
    print "Binance: default_on_error"


def default_on_public(exchange_id, args):
    print "Binance: odefault_on_public:"
    print exchange_id, args


class SubscriptionBinance:
    def __init__(self, pair_id, local_cache, on_update=default_on_public, on_any_issue=default_on_error, base_url=BinanceParameters.URL):
        """
        :param pair_id:         - currency pair to be used for trading
        :param on_update:       - idea is the following:
                                    we pass reference to method WITH initialized order book for that pair_id
                                    whenever we receive update we update order book and trigger checks for arbitrage
        :param base_url:        - web-socket subscription end points
        :param updates_queue:   - queue to accumulation of updates
        """

        self.url = base_url

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_binance(self.pair_id).lower()

        self.local_cache = local_cache

        self.subscription_url = BinanceParameters.SUBSCRIBE_UPDATE.format(pair_name=self.pair_name)

        self.on_update = on_update
        self.on_any_issue = on_any_issue

    def on_open(self, ws):
        print "Opening connection..."

    def on_close(self, ws):
        ws.close()

        msg = "Binance - triggered on_close. We have to re-init the whole state from the scratch"
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        self.on_any_issue()

    def on_public(self, ws, args):
        msg = process_message(args)
        order_book_delta = parse_socket_update_binance(msg)

        if order_book_delta is None:
            err_msg = "Binance - cant parse update from message: {msg}".format(msg=msg)
            log_to_file(err_msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            self.on_update(EXCHANGE.BINANCE, order_book_delta)

    def on_error(self, ws, error):
        die_hard("Binance - triggered on_error - {err}. We have to re-init the whole state from the scratch - "
                 "which is not implemented".format(err=error))

        self.on_any_issue()

    def subscribe(self):

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        final_url = BinanceParameters.URL + self.subscription_url

        # Create connection
        while True:
            try:
                self.ws = create_connection(final_url)
                self.ws.settimeout(15)
                break
            except Exception as e:
                print('Binance - connect ws error - {}, retry...'.format(str(e)))
                sleep_for(5)

        # actual subscription - for binance can be embedded within url
        # self.ws.send(self.subscription_url)

        # event loop
        while self.local_cache.get_value("SYNC_STAGE") != ORDER_BOOK_SYNC_STAGES.RESETTING:
            try:
                compressData = self.ws.recv()
                self.on_public(self.ws, compressData)
            except Exception as e:      # Supposedly timeout big enough to not trigger re-syncing
                msg = "Binance - triggered exception during reading from socket = {}. Reseting stage!".format(str(e))
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                print msg

                self.local_cache.set_value("SYNC_STAGE", ORDER_BOOK_SYNC_STAGES.RESETTING)

                break

        msg = "Binance - exit from main loop. Current thread will be finished."
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    def subscribe_app(self):
        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        final_url = BinanceParameters.URL + self.subscription_url

        self.ws = websocket.WebSocketApp(final_url,
                                    on_message=self.on_public,
                                    on_error=self.on_error,
                                    on_close=self.on_close)

        self.ws.on_open = self.on_open

        self.ws.run_forever(ping_interval=10)

    def disconnect(self):
        self.ws.close()
