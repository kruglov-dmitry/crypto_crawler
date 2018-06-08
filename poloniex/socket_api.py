import websocket
import json
import time
import thread

from poloniex.currency_utils import get_currency_pair_to_poloniex
from enums.exchange import EXCHANGE


def process_message(compressData):
    return compressData


class PoloniexParameters:
    URL = "wss://api2.poloniex.com/"

    SUBSCRIBE_TROLL_BOX = 1001
    SUBSCRIBE_TICKER = 1002
    SUBSCRIBE_BASE_COIN_24HR_STATS = 1003
    SUBSCRIBE_HEARTBEAT = 1010


def default_on_public(args):
    print "on_public", args
    msg = process_message(args)
    print msg


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


class SubscriptionPoloniex:
    def __init__(self, pair_id, on_update=default_on_public, base_url=PoloniexParameters.URL):
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
        self.pair_name = get_currency_pair_to_poloniex(self.pair_id)

        self.on_update = on_update

    def on_open(self, ws):
        print("ONOPEN")

        def run(ws):
            ws.send(json.dumps({'command': 'subscribe', 'channel': PoloniexParameters.SUBSCRIBE_HEARTBEAT}))
            # ws.send(json.dumps({'command': 'subscribe', 'channel': PoloniexParameters.SUBSCRIBE_TICKER}))
            ws.send(json.dumps({'command': 'subscribe', 'channel': self.pair_name}))
            ws.send(json.dumps({'command': 'subscribe', 'channel': self.pair_name}))
            while True:
                time.sleep(1)
            ws.close()
            print("thread terminating...")

        thread.start_new_thread(run, (ws,))

    def on_public(self, ws, args):
        msg = process_message(args)
        self.on_update(EXCHANGE.POLONIEX, msg)

    def subscribe(self):
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(PoloniexParameters.URL,
                                    on_message=self.on_public,
                                    on_error=self.subscribe,
                                    on_close=on_close)
        ws.on_open = self.on_open
        ws.run_forever()
