import websocket
from websocket import create_connection
import json
import thread
import ssl
import zlib
import uuid

from huobi.currency_utils import get_currency_pair_to_huobi
from enums.exchange import EXCHANGE

from data.OrderBook import OrderBook
from data.Deal import Deal

from utils.time_utils import get_now_seconds_utc_ms, sleep_for
from utils.file_utils import log_to_file
from debug_utils import get_logging_level, LOG_ALL_TRACE, SOCKET_ERRORS_LOG_FILE_NAME

from logging_tools.socket_logging import log_conect_to_websocket, log_error_on_receive_from_socket, \
    log_subscription_cancelled, log_websocket_disconnect, log_send_heart_beat_failed


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


def process_message(compress_data):
    try:
        return json.loads(zlib.decompress(compress_data, 16 + zlib.MAX_WBITS))
    except:
        log_to_file(compress_data, "huobi.log")


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

        self.should_run = False

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

        print("Huobi: Opening connection...")

        def run():
            self.ws.send(self.subscription_url)
            try:
                while self.should_run:
                    self.ws.send(json.dumps({'ping': 18212558000}))
                    sleep_for(1)
                self.ws.close()
            except Exception as e:
                log_send_heart_beat_failed("Huobi", e)

        thread.start_new_thread(run, ())

    def subscribe(self):

        self.should_run = True

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        # Create connection
        try:
            self.ws = create_connection(HuobiParameters.URL, enable_multithread=True, sslopt={"cert_reqs": ssl.CERT_NONE})
            self.ws.settimeout(15)
        except Exception as e:
            print('Huobi - connect ws error - {}, retry...'.format(str(e)))

            self.disconnect()

            return

        # actual subscription in dedicated thread
        self.on_open()

        log_conect_to_websocket("Huobi")

        # event loop
        while self.should_run:
            try:
                compress_data = self.ws.recv()
                if compress_data:
                    self.on_public(compress_data)
            except Exception as e:

                log_error_on_receive_from_socket("Huobi", e)

                break

        log_subscription_cancelled("Huobi")

        self.disconnect()

    def disconnect(self):
        self.should_run = False

        try:
            self.ws.close()
        except Exception as e:
            log_websocket_disconnect("Huobi", e)

    def is_running(self):
        return self.should_run
