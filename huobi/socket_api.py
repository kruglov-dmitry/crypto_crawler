import json
import thread
import ssl
import zlib
import uuid
import websocket
from websocket import create_connection

from huobi.currency_utils import get_currency_pair_to_huobi
from huobi.constants import HUOBI_WEBSOCKET_URL, HUOBI_SUBSCRIPTION_STRING
from enums.exchange import EXCHANGE

from data.order_book import OrderBook
from data.deal import Deal

from utils.time_utils import get_now_seconds_utc_ms, sleep_for
from utils.file_utils import log_to_file
from utils.system_utils import die_hard
from utils.debug_utils import get_logging_level, LOG_ALL_TRACE, SOCKET_ERRORS_LOG_FILE_NAME, LOG_ALL_DEBUG

from logging_tools.socket_logging import log_conect_to_websocket, log_error_on_receive_from_socket, \
    log_subscription_cancelled, log_websocket_disconnect, log_send_heart_beat_failed, \
    log_subscribe_to_exchange_heartbeat, log_unsubscribe_to_exchange_heartbeat


def parse_socket_update_huobi(order_book_delta, pair_id):
    if "tick" not in order_book_delta:
        return None

    order_book_delta = order_book_delta["tick"]

    sequence_id = long(order_book_delta["version"])

    asks = [Deal(price=b[0], volume=b[1]) for b in order_book_delta.get("asks", [])]
    bids = [Deal(price=b[0], volume=b[1]) for b in order_book_delta.get("bids", [])]

    timest_ms = get_now_seconds_utc_ms()
        
    return OrderBook(pair_id, timest_ms, asks, bids, EXCHANGE.HUOBI, sequence_id)


def process_message(compress_data):
    try:
        return json.loads(zlib.decompress(compress_data, 16 + zlib.MAX_WBITS))
    except Exception as e:
        log_to_file(e, "huobi.log")
        log_to_file(compress_data, "huobi.log")


def default_on_public(exchange_id, args):
    if get_logging_level() >= LOG_ALL_DEBUG:
        print("on_public")
        print("".join([str(exchange_id), str(args)]))


def default_on_error(ws, error):
    ws.close()
    print(error)


class SubscriptionHuobi(object):
    def __init__(self, pair_id, on_update=default_on_public, base_url=HUOBI_WEBSOCKET_URL):
        """
        :param pair_id:     - currency pair to be used for trading
        :param base_url:    - web-socket subscription end points
        :param on_update:   - idea is the following:
            we pass reference to method WITH initialized order book for that pair_id
            whenever we receive update we update order book and trigger checks for arbitrage
        """

        self.url = base_url

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_huobi(self.pair_id)

        self.subscription_url = HUOBI_SUBSCRIPTION_STRING.format(
            pair_name=self.pair_name, uuid_id=uuid.uuid4())

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

        def run():
            log_subscribe_to_exchange_heartbeat("Huobi")
            self.ws.send(self.subscription_url)
            try:
                while self.should_run:
                    self.ws.send(json.dumps({'ping': 18212558000}))
                    sleep_for(1)
                self.ws.close()
            except Exception as e:
                log_send_heart_beat_failed("Huobi", e)

            log_unsubscribe_to_exchange_heartbeat("Huobi")

        thread.start_new_thread(run, ())

    def subscribe(self):

        if self.should_run:
            die_hard("Huobi - another subcription thread running?")

        self.should_run = True

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        # Create connection
        try:
            self.ws = create_connection(HUOBI_WEBSOCKET_URL, enable_multithread=True, sslopt={"cert_reqs": ssl.CERT_NONE})
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
