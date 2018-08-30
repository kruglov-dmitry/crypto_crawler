from json import loads
import websocket

from binance.currency_utils import get_currency_pair_to_binance
from enums.exchange import EXCHANGE
from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal


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

    sequence_id = long(order_book_delta["U"])

    asks = []
    bids = []
    trades_sell = []
    trades_buy = []

    for a in order_book_delta["a"]:
        asks.append(Deal(a[0], a[1]))

    for a in order_book_delta["b"]:
        bids.append(Deal(a[0], a[1]))

    return OrderBookUpdate(sequence_id, bids, asks, trades_sell, trades_buy)


def process_message(compressData):
    return loads(compressData)


class BinanceParameters:
    URL = "wss://stream.binance.com:9443/ws/"

    SUBSCRIBE_UPDATE = "{pair_name}@depth"


def default_on_public(exchange_id, args, updates_queue):
    msg = process_message(args)
    print exchange_id, msg, updates_queue


class SubscriptionBinance:
    def __init__(self, pair_id, on_update=default_on_public, base_url=BinanceParameters.URL, updates_queue=None):
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

        self.subscription_url = BinanceParameters.SUBSCRIBE_UPDATE.format(pair_name=self.pair_name)

        self.on_update = on_update
        self.updates_queue = updates_queue

    def on_open(self, ws):
        print "Opening connection..."

    def on_close(self, ws):
        print("Connection closed, Reconnecting...")
        self.subscribe()

    def on_public(self, ws, args):
        msg = process_message(args)
        self.on_update(EXCHANGE.BINANCE, msg, self.updates_queue)

    def on_error(self, ws, error):
        print "Error: ", error
        self.subscribe()

    def subscribe(self):
        # websocket.enableTrace(True)
        final_url = BinanceParameters.URL+self.subscription_url
        print final_url
        ws = websocket.WebSocketApp(final_url,
                                    on_message=self.on_public,
                                    on_error=self.subscribe,
                                    on_close=self.on_close)

        ws.on_open = self.on_open

        ws.run_forever()
