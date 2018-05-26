import websocket

from binance.currency_utils import get_currency_pair_to_binance


def process_message(compressData):
    return compressData


class BinanceParameters:
    URL = "wss://stream.binance.com:9443/ws/"

    SUBSCRIBE_UPDATE = "{pair_name}@depth"


def default_on_public(args):
    print "on_public", args
    msg = process_message(args)
    print msg


class SubscriptionBinance:
    def __init__(self, pair_id, on_update=default_on_public, base_url=BinanceParameters.URL):
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
        self.pair_name = get_currency_pair_to_binance(self.pair_id)

        self.subscription_url = BinanceParameters.SUBSCRIBE_UPDATE.format(pair_name=self.pair_name)

        self.on_update = on_update

    def on_open(self, ws):
        print("ONOPEN")

    def on_close(ws):
        print("### closed ###")

    def on_public(self, args):
        print "on_public", args
        msg = process_message(args)
        self.on_update(msg)

    def subscribe(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(BinanceParameters.URL+self.subscription_url,
                                    on_message=self.on_public,
                                    on_error=self.subscribe,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()
