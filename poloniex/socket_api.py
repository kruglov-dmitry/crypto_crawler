# coding=utf-8
from json import loads
import websocket
from websocket import create_connection
import json
import time
import thread

from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc_ms, sleep_for

from poloniex.currency_utils import get_currency_pair_to_poloniex
from enums.exchange import EXCHANGE
from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

from data.OrderBookUpdate import OrderBookUpdate
from data.Deal import Deal
from data.OrderBook import OrderBook

from debug_utils import SOCKET_ERRORS_LOG_FILE_NAME, get_logging_level, LOG_ALL_TRACE
from utils.system_utils import die_hard


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


def parse_socket_order_book_poloniex(order_book_snapshot, pair_id):
    """

    :param order_book_snapshot:

    [
        <channel id>,
        <sequence number>,
        [
            [
                "i",
                    {
                        "currencyPair": "<currency pair name>",
                        "orderBook": [
                        {
                            "<lowest ask price>": "<lowest ask size>",
                            "<next ask price>": "<next ask size>",
                            …
                        },
                        {
                            "<highest bid price>": "<highest bid size>",
                            "<next bid price>": "<next bid size>",
                            …
                        }
                        ]
                    }
            ]
        ]
    ]


    order_book_snapshot[2][0][1]["orderBook"][0]

    Example:
    [
        148,
        573963482,
        [
            [
                "i",
                {
                    "currencyPair": "BTC_ETH",
                    "orderBook": [
                    {
                        "0.08964203": "0.00225904",
                        "0.04069708": "15.37598559",
                        ...
                    },
                     {
                        "0.03496358": "0.32591524",
                        "0.02020000": "0.50000000",
                        ...
                    }
                    ]
                }
            ]
        ]
    ]

    :param pair_id:
    :return:
    """

    timest_ms = get_now_seconds_utc_ms()

    sequence_id = long(order_book_snapshot[1])

    asks = []
    for k, v in order_book_snapshot[2][0][1]["orderBook"][0].iteritems():
        asks.append(Deal(k, v))

    bids = []
    for k, v in order_book_snapshot[2][0][1]["orderBook"][1].iteritems():
        bids.append(Deal(k, v))

    return OrderBook(pair_id, timest_ms, asks, bids, EXCHANGE.POLONIEX, sequence_id)


def parse_socket_update_poloniex(order_book_delta):
    """
                Message format for ticker
                [
                    1002,                             Channel
                    null,                             Unknown
                    [
                        121,                          CurrencyPairID
                        "10777.56054438",             Last
                        "10800.00000000",             lowestAsk
                        "10789.20000001",             highestBid
                        "-0.00860373",                percentChange
                        "72542984.79776118",          baseVolume
                        "6792.60163706",              quoteVolume
                        0,                            isForzen
                        "11400.00000000",             high24hr
                        "9880.00000009"               low24hr
                    ]
                ]

                [1002,null,[158,"0.00052808","0.00053854","0.00052926","0.05571659","4.07923480","7302.01523251",0,"0.00061600","0.00049471"]]

                So the columns for orders are
                    messageType -> t/trade, o/order
                    tradeID -> only for trades, just a number
                    orderType -> 1/bid,0/ask
                    rate
                    amount
                    time
                    sequence
                148 is code for BTCETH, yeah there is no documentation.. but when trades occur You can figure out.
                Bid is always 1, cause You add something new..

                PairId, Nonce, orders\trades deltas:
                [24,219199090,[["o",1,"0.04122908","0.01636493"],["t","10026908",0,"0.04122908","0.00105314",1527880700]]]
                [24,219201009,[["o",0,"0.04111587","0.00000000"],["o",0,"0.04111174","1.52701255"]]]
                [24,219164304,[["o",1,"0.04064791","0.01435233"],["o",1,"0.04068034","0.16858384"]]]

                :param order_book_delta:
                :return:
            """

    asks = []
    bids = []
    trades_sell = []
    trades_buy = []

    # We suppose that bid and ask are sorted in particular order:
    # for bids - highest - first
    # for asks - lowest - first
    if len(order_book_delta) < 3:
        return None

    timest_ms = get_now_seconds_utc_ms()

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

    # FIXME NOTE: during update we are not using trades_sell\trades_buy at all - so probably
    # better not to use them at all

    return OrderBookUpdate(sequence_id, bids, asks, timest_ms, trades_sell, trades_buy)


def process_message(compressData):
    return loads(compressData)


def default_on_public(exchange_id, args):
    print("Poloniex: default_on_public")
    print exchange_id, args


def default_on_error():
    print("Poloniex: default_on_error")


def default_on_close():
    print("Poloniex: default_on_close")


class SubscriptionPoloniex:
    def __init__(self, pair_id, local_cache, on_update=default_on_public, on_any_issue=default_on_error, base_url=PoloniexParameters.URL):
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

        self.local_cache = local_cache

        self.on_update = on_update

        self.on_any_issue = on_any_issue

        self.order_book_is_received = False

    def on_open(self, ws):

        print "Opening connection..."

        def run(ws):
            ws.send(json.dumps({'command': 'subscribe', 'channel': PoloniexParameters.SUBSCRIBE_HEARTBEAT}))
            ws.send(json.dumps({'command': 'subscribe', 'channel': self.pair_name}))
            while True:
                time.sleep(1)
            ws.close()
            print("thread terminating...")

        thread.start_new_thread(run, (ws,))

    def on_public(self, ws, args):
        msg = process_message(args)
        if not self.order_book_is_received and "orderBook" in args:      # FIXME Howdy DK - is this check promissing FAST?
            self.order_book_is_received = True
            order_book_delta = parse_socket_order_book_poloniex(msg, self.pair_id)
        else:
            order_book_delta = parse_socket_update_poloniex(msg)

        if order_book_delta is None:
            # Poloniex tend to send heartbeat messages: [1010]
            if "1010" not in str(msg):
                err_msg = "Poloniex - cant parse update from message: {msg}".format(msg=msg)
                log_to_file(err_msg, SOCKET_ERRORS_LOG_FILE_NAME)
        else:
            self.on_update(EXCHANGE.POLONIEX, order_book_delta)

    def on_close(self, ws):

        ws.close()

        msg = "Poloniex - triggered on_close. We have to re-init the whole state from the scratch"
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        self.on_any_issue()

    def on_error(self, ws, error):

        ws.close()

        msg = "Poloniex - triggered on_error - {err}. We have to re-init the whole state from the scratch - which is " \
              "not implemented".format(err=error)
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        self.on_any_issue()

    def subscribe(self):
        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        # Create connection
        while True:
            try:
                self.ws = create_connection(PoloniexParameters.URL)
                self.ws.settimeout(15)
                break
            except Exception as e:
                print('Poloniex - connect ws error - {}, retry...'.format(str(e)))
                sleep_for(5)

        # actual subscription
        self.on_open(self.ws)

        # event loop
        while int(self.local_cache.get_value("SYNC_STAGE")) != ORDER_BOOK_SYNC_STAGES.RESETTING:
            try:
                compressData = self.ws.recv()
                self.on_public(self.ws, compressData)
            except Exception as e:  # Supposedly timeout big enough to not trigger re-syncing
                msg = "Poloniex - triggered exception during reading from socket = {}. Reseting stage!".format(str(e))
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                print msg

                self.local_cache.set_value("SYNC_STAGE", ORDER_BOOK_SYNC_STAGES.RESETTING)

                break

        msg = "Poloniex - exit from main loop. Current thread will be finished."
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    def subscribe_app(self):

        if get_logging_level() == LOG_ALL_TRACE:
            websocket.enableTrace(True)

        self.ws = websocket.WebSocketApp(PoloniexParameters.URL,
                                    on_message=self.on_public,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever(ping_interval=10)

    def disconnect(self):
        self.ws.close()
