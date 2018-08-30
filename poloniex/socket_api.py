from json import loads
import websocket
import json
import time
import thread

from utils.file_utils import log_to_file

from poloniex.currency_utils import get_currency_pair_to_poloniex
from enums.exchange import EXCHANGE
from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal

from debug_utils import SOCKET_ERRORS_LOG_FILE_NAME


class PoloniexParameters:
    URL = "wss://api2.poloniex.com/"

    SUBSCRIBE_TROLL_BOX = 1001
    SUBSCRIBE_TICKER = 1002
    SUBSCRIBE_BASE_COIN_24HR_STATS = 1003
    SUBSCRIBE_HEARTBEAT = 1010

    POLONIEX_ORDER = "o"
    POLONIEX_TRADE = "t"

    POLONIEX_ORDER_BID = 1
    POLONIEX_ORDER_ASK = 0


def parse_socket_update_poloniex(order_book_delta):

    asks = []
    bids = []
    trades_sell = []
    trades_buy = []

    # We suppose that bid and ask are sorted in particular order:
    # for bids - highest - first
    # for asks - lowest - first
    if len(order_book_delta) < 3:
        return None

    sequence_id = long(order_book_delta[1])

    delta = order_book_delta[2]
    for entry in delta:
        if entry[0] == PoloniexParameters.POLONIEX_ORDER:
            new_deal = Deal(entry[2], entry[3])

            # If it is just orders - we insert in a way to keep sorted order
            if entry[1] == PoloniexParameters.POLONIEX_ORDER_ASK:
                asks.append(new_deal)
            elif entry[1] == PoloniexParameters.POLONIEX_ORDER_BID:
                bids.append(new_deal)
            else:
                msg = "Poloniex socket update parsing - {wtf} total: {ttt}".format(wtf=entry, ttt=order_book_delta)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
        elif entry[0] == PoloniexParameters.POLONIEX_TRADE:

            # FIXME NOTE:   this is ugly hack to avoid creation of custom objects
            #               and at the same Deal object contains lt method that
            #               used by bisect for efficient binary search in sorted list
            new_deal = Deal(entry[3], entry[4])

            # For trade - vice-versa we should update opposite arrays:
            # in case we have trade with type bid -> we will update orders at ask
            # in case we have trade with type ask -> we will update orders at bid

            if entry[2] == PoloniexParameters.POLONIEX_ORDER_BID:
                trades_sell.append(new_deal)
            elif entry[2] == PoloniexParameters.POLONIEX_ORDER_ASK:
                trades_buy.append(new_deal)
            else:
                msg = "Poloniex socket update parsing - {wtf}".format(wtf=entry)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            msg = "Poloniex socket update parsing - UNKNOWN TYPE - {wtf}".format(wtf=entry)
            log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    return OrderBookUpdate(sequence_id, bids, asks, trades_sell, trades_buy)


def process_message(compressData):
    return loads(compressData)


def default_on_public(exchange_id, args, updates_queue):
    msg = process_message(args)
    print exchange_id, msg, updates_queue


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


class SubscriptionPoloniex:
    def __init__(self, pair_id, on_update=default_on_public, base_url=PoloniexParameters.URL, updates_queue=None):
        """
        :param pair_id:     - currency pair to be used for trading
        :param base_url:    - web-socket subscription end points
        :param on_update:   - idea is the following:
            we pass reference to method WITH initialized order book for that pair_id
            whenever we receive update we update order book and trigger checks for arbitrage
        """

        self.url = base_url

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_poloniex(self.pair_id)

        self.on_update = on_update
        self.updates_queue = updates_queue

    def on_open(self, ws):

        print "Opening connection..."

        def run(ws):
            ws.send(json.dumps({'command': 'subscribe', 'channel': PoloniexParameters.SUBSCRIBE_HEARTBEAT}))
            # ws.send(json.dumps({'command': 'subscribe', 'channel': PoloniexParameters.SUBSCRIBE_TICKER}))
            ws.send(json.dumps({'command': 'subscribe', 'channel': self.pair_name}))
            while True:
                time.sleep(1)
            ws.close()
            print("thread terminating...")

        thread.start_new_thread(run, (ws,))

    def on_public(self, ws, args):
        msg = process_message(args)
        self.on_update(EXCHANGE.POLONIEX, msg, self.updates_queue)

    def on_close(self, ws, args):
        print("Connection closed, Reconnecting...")
        self.subscribe()

    def subscribe(self):
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(PoloniexParameters.URL,
                                    on_message=self.on_public,
                                    on_error=self.subscribe,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()
