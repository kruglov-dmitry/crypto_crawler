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
from services.sync_stage import set_stage, get_stage

import time
import thread


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
    try:
        return loads(zlib.decompress(compressData, 16 + zlib.MAX_WBITS))
    except:
        log_to_file(compressData, "U.log")


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
    def __init__(self, pair_id, on_update=default_on_public, base_url=HuobiParameters.URL):
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

        self.should_run = True

    def on_public(self, args):
        msg = process_message(args)
        updated_order_book = parse_socket_update_huobi(msg, self.pair_id)
        if updated_order_book is None:
            # Huobi tend to send heartbeat or confirmation of subscription
            # {u'ping': 1537212403003}
            # {u'status': u'ok',
            # u'id': u'fbeeaf31-f0bc-4fa0-b704-95134aae9b81',
            # u'ts': 1537212402856,
            # u'subbed': u'market.dashbtc.depth.step0'}
            if "ping" in msg or "pong" in msg or ("status" in msg and "ok" == msg["status"]):
                return
            err_msg = "Huobi - cant parse update from message: {msg}".format(msg=msg)
            log_to_file(err_msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            self.on_update(EXCHANGE.HUOBI, updated_order_book)

    def on_open(self):
        import json

        print("Huobi: Opening connection...")

        self.ws.send(self.subscription_url)

        def run():
            try:
                while True:
                    if get_stage() == ORDER_BOOK_SYNC_STAGES.RESETTING:
                        break
                    self.ws.send(json.dumps({'ping': 18212558000}))
                    time.sleep(1)
                self.ws.close()
            except Exception as e:
                msg = "Huobi: connection terminated with error: {er}".format(er=str(e))
                print(msg)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            set_stage(ORDER_BOOK_SYNC_STAGES.RESETTING)

        thread.start_new_thread(run, ())

    def subscribe(self):

        self.should_run = True

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        # Create connection
        while True:
            try:
                self.ws = create_connection(HuobiParameters.URL, enable_multithread=True, sslopt={"cert_reqs": ssl.CERT_NONE})
                self.ws.settimeout(15)
                break
            except Exception as e:
                print('Huobi - connect ws error - {}, retry...'.format(str(e)))
                sleep_for(5)

        # actual subscription in dedicated thread
        self.on_open()

        msg = "Huobi - before main loop..."
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
        # event loop
        while self.should_run:
            try:
                compressData = self.ws.recv()
                if compressData:
                    self.on_public(compressData)
            except Exception as e:  # Supposedly timeout big enough to not trigger re-syncing
                msg = "Huobi - triggered exception during reading from socket = {}. Reseting stage!".format(str(e))
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                print msg
                self.should_run = False

                set_stage(ORDER_BOOK_SYNC_STAGES.RESETTING)

                break

        msg = "Huobi - exit from main loop. Current thread will be finished."
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        self.disconnect()

    def disconnect(self):
        self.should_run = False

        sleep_for(3)  # To wait till all processing be ended

        try:
            self.ws.close()
        except Exception as e:
            msg = "Binance - triggered exception during closing socket = {} at disconnect!".format(str(e))
            log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            print msg

    def is_running(self):
        return self.should_run
