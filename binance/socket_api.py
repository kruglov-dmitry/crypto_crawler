from json import loads
import websocket

from binance.currency_utils import get_currency_pair_to_binance
from enums.exchange import EXCHANGE


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
