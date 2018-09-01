from json import loads
import websocket
import ssl

import zlib
import uuid

from huobi.currency_utils import get_currency_pair_to_huobi
from enums.exchange import EXCHANGE

from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal

from utils.time_utils import get_now_seconds_utc_ms


def parse_socket_update_huobi(order_book_delta):
    if "tick" in order_book_delta:

        sequence_id = long(order_book_delta["version"])
        asks = []
        bids = []
        trades_sell = []
        trades_buy = []

        if "asks" in order_book_delta:
            for b in order_book_delta["asks"]:
                asks.append(Deal(price=b[0], volume=b[1]))

        if "bids" in order_book_delta:
            for b in order_book_delta["bids"]:
                bids.append(Deal(price=b[0], volume=b[1]))

        timest_ms = get_now_seconds_utc_ms()

        return OrderBookUpdate(sequence_id, bids, asks, timest_ms, trades_sell, trades_buy)
    else:
        return None


def process_message(compressData):
    return loads(zlib.decompress(compressData, 16 + zlib.MAX_WBITS))


class HuobiParameters:
    URL = "wss://api.huobipro.com/ws"
    SUBSCRIPTION_STRING = """{{"sub": "market.{pair_name}.depth.step0","id": "{uuid_id}"}}"""


def default_on_public(exchange_id, args, updates_queue):
    print "on_public"
    print exchange_id, args, updates_queue


class SubscriptionHuobi:
    def __init__(self, pair_id, on_update=default_on_public, base_url=HuobiParameters.URL, updates_queue=None):
        """
        :param pair_id:     - currency pair to be used for trading
        :param base_url:    - web-socket subscription end points
        :param on_receive:  - pass
        :param on_error:    - recconect
        :param on_update:   - idea is the following:
            we pass reference to method WITH initialized order book for that pair_id
            whenever we receive update we update order book and trigger checks for arbitrage
        """

        self.url = base_url

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_huobi(self.pair_id)

        self.subscription_url = HuobiParameters.SUBSCRIPTION_STRING.format(pair_name=self.pair_name, uuid_id=uuid.uuid4())

        self.on_update = on_update
        self.updates_queue = updates_queue

    def on_public(self, ws, args):
        msg = process_message(args)
        updated_order_book = parse_socket_update_huobi(msg)
        self.on_update(EXCHANGE.HUOBI, updated_order_book, self.updates_queue)

    def on_error(self, ws, error):
        print "Error:", error
        self.subscribe()

    def on_close(self, ws):
        print("Connection closed, Reconnecting...")
        self.subscribe()

    def on_open(self, ws):

        print "Opening connection..."

        ws.send(self.subscription_url)

        #  compressData=ws.recv()
        #  print "CONFIRMATION OF SUBSCRIPTION:", process_message(compressData)

    def subscribe(self):

        # websocket.enableTrace(True)

        ws = websocket.WebSocketApp(HuobiParameters.URL,
                                    on_message=self.on_public,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
