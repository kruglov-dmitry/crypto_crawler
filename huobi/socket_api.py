from json import loads
import websocket
from websocket import create_connection
import ssl

import zlib
import uuid

from huobi.currency_utils import get_currency_pair_to_huobi
from enums.exchange import EXCHANGE
from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

from data.OrderBook import OrderBook
from data.Deal import Deal

from utils.time_utils import get_now_seconds_utc_ms, sleep_for
from utils.file_utils import log_to_file
from debug_utils import get_logging_level, LOG_ALL_TRACE, SOCKET_ERRORS_LOG_FILE_NAME


def parse_socket_update_huobi(order_book_delta, pair_id):
    if "tick" in order_book_delta:

        order_book_delta = order_book_delta["tick"]

        sequence_id = long(order_book_delta["version"])
        asks = []
        bids = []

        if "asks" in order_book_delta:
            for b in order_book_delta["asks"]:
                asks.append(Deal(price=b[0], volume=b[1]))

        if "bids" in order_book_delta:
            for b in order_book_delta["bids"]:
                bids.append(Deal(price=b[0], volume=b[1]))

        timest_ms = get_now_seconds_utc_ms()
        
        return OrderBook(pair_id, timest_ms, asks, bids, EXCHANGE.HUOBI, sequence_id)

    else:
        return None


def process_message(compressData):
    return loads(zlib.decompress(compressData, 16 + zlib.MAX_WBITS))


class HuobiParameters:
    URL = "wss://api.huobipro.com/ws"
    SUBSCRIPTION_STRING = """{{"sub": "market.{pair_name}.depth.step0","id": "{uuid_id}"}}"""


def default_on_public(exchange_id, args):
    print "on_public"
    print exchange_id, args


def default_on_error(ws, error):
    ws.close()
    print(error)


class SubscriptionHuobi:
    def __init__(self, pair_id, local_cache, on_update=default_on_public, on_any_issue=default_on_error, base_url=HuobiParameters.URL):
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

        self.local_cache = local_cache

        self.subscription_url = HuobiParameters.SUBSCRIPTION_STRING.format(pair_name=self.pair_name, uuid_id=uuid.uuid4())

        self.on_update = on_update
        self.on_any_issue = on_any_issue

    def on_public(self, ws, args):
        msg = process_message(args)
        updated_order_book = parse_socket_update_huobi(msg, self.pair_id)
        if updated_order_book is None:
            # Huobi tend to send heartbeat or confirmation of subscription
            # {u'ping': 1537212403003}
            # {u'status': u'ok',
            # u'id': u'fbeeaf31-f0bc-4fa0-b704-95134aae9b81',
            # u'ts': 1537212402856,
            # u'subbed': u'market.dashbtc.depth.step0'}
            if "ping" in msg or ("status" in msg and "ok" == msg["status"]):
                return
            err_msg = "Huobi - cant parse update from message: {msg}".format(msg=msg)
            log_to_file(err_msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            self.on_update(EXCHANGE.HUOBI, updated_order_book)

    def on_error(self, ws, error):
        # DK NOTE:  it is fine here - as Huobi sent the full order book
        #           so no need to do synchronisation

        msg = "Huobi triggered on_error: {err}".format(err=error)
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
        ws.close()

        sleep_for(1)
        self.subscribe()

    def on_close(self, ws):
        # DK NOTE:  it is fine here - as Huobi sent the full order book
        #           so no need to do synchronisation

        msg = "Huobi - Connection closed, Reconnecting..."
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        ws.close()

        sleep_for(1)
        self.subscribe()

    def on_open(self, ws):

        print "Opening connection..."

        ws.send(self.subscription_url)

    def subscribe(self):

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        # Create connection
        while True:
            try:
                self.ws = create_connection(HuobiParameters.URL, sslopt={"cert_reqs": ssl.CERT_NONE})
                self.ws.settimeout(15)
                break
            except Exception as e:
                print('Huobi - connect ws error - {}, retry...'.format(str(e)))
                sleep_for(5)

        # actual subscription
        self.on_open(self.ws)

        # event loop
        while self.local_cache.get_value("SYNC_STAGE") != ORDER_BOOK_SYNC_STAGES.RESETTING:
            try:
                compressData = self.ws.recv()
                self.on_public(self.ws, compressData)
            except Exception as e:  # Supposedly timeout big enough to not trigger re-syncing
                msg = "Huobi - triggered exception during reading from socket = {}. Reseting stage!".format(str(e))
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                print msg

                self.local_cache.set_value("SYNC_STAGE", ORDER_BOOK_SYNC_STAGES.RESETTING)

                break

        msg = "Huobi - exit from main loop. Current thread will be finished."
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    def subscribe_app(self):
        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        self.ws = websocket.WebSocketApp(HuobiParameters.URL,
                                    on_message=self.on_public,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.ws.run_forever(ping_interval=10, sslopt={"cert_reqs": ssl.CERT_NONE})

    def disconnect(self):
        self.ws.close()
