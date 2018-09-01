import re
from utils.currency_utils import get_pair_name_by_id

from bittrex.currency_utils import get_currency_pair_from_bittrex
from kraken.currency_utils import get_currency_pair_from_kraken
from poloniex.currency_utils import get_currency_pair_from_poloniex
from binance.currency_utils import get_currency_pair_from_binance
from huobi.currency_utils import get_currency_pair_to_huobi, get_currency_pair_from_huobi

from analysis.binary_search import binary_search

from BaseData import BaseData
from Deal import Deal

from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE

from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import get_now_seconds_utc_ms, get_date_time_from_epoch
from utils.file_utils import log_to_file

from constants import MAX_VOLUME_ORDER_BOOK, FLOAT_POINT_PRECISION
from debug_utils import SOCKET_ERRORS_LOG_FILE_NAME

# FIXME NOTE - not the smartest idea to deal with
regex_string = "\[exchange - (.*) exchange_id - (.*) pair - (.*) pair_id - (.*) timest - (.*) bids - (.*) asks - (.*)\]"
regex = re.compile(regex_string)

deal_array_regex_string = "price - ([0-9]*.[0-9e-]*) volume - ([0-9]*.[0-9e-]*)"
deal_array_regex = re.compile(deal_array_regex_string)

ORDER_BOOK_TYPE_NAME = "order_book"

ORDER_BOOK_INSERT_BIDS = "insert into order_book_bid(order_book_id, price, volume) values (%s, %s, %s);"
ORDER_BOOK_INSERT_ASKS = "insert into order_book_ask(order_book_id, price, volume) values (%s, %s, %s);"

ORDER_BOOK_TABLE_NAME = "order_book"
ORDER_BOOK_COLUMNS = ("pair_id", "exchange_id", "timest", "date_time")
ORDER_BOOK_INSERT_QUERY = """insert into {table_name} ({columns}) values(%s, %s, %s, %s) returning id;""".format(
    table_name=ORDER_BOOK_TABLE_NAME, columns=','.join(ORDER_BOOK_COLUMNS))

TICKER_TYPE_NAME = "ticker"


def cmp_method_ask(a, b):
    return a.price < b.price


def cmp_method_bid(a, b):
    return a.price > b.price


class OrderBook(BaseData):
    insert_query = ORDER_BOOK_INSERT_QUERY
    type = ORDER_BOOK_TYPE_NAME

    table_name = ORDER_BOOK_TABLE_NAME
    columns = ORDER_BOOK_COLUMNS

    def __init__(self, pair_id, timest, sell_bids, buy_bids, exchange_id, sequence_id=None):
        # FIXME NOTE - various volume data?
        self.pair_id = int(pair_id)
        self.pair_name = get_pair_name_by_id(self.pair_id)
        self.timest = timest
        self.ask = sell_bids
        self.bid = buy_bids
        self.exchange_id = int(exchange_id)
        self.exchange = get_exchange_name_by_id(self.exchange_id)
        self.sequence_id = sequence_id

    def sort_by_price(self):
        self.bid = sorted(self.bid, key=lambda x: x.price, reverse=True)        # highest - first
        self.ask = sorted(self.ask, key=lambda x: x.price, reverse=False)       # lowest - first

    def get_pg_arg_list(self):
        return (self.pair_id,
                self.exchange_id,
                self.timest,
                get_date_time_from_epoch(self.timest)
                )

    def __str__(self):
        attr_list = [a for a in dir(self) if not a.startswith('__') and
                     not a.startswith("ask") and not a.startswith("bid") and
                     not a.startswith("insert") and not callable(getattr(self, a))]
        str_repr = "["
        for every_attr in attr_list:
            str_repr += every_attr + " - " + str(getattr(self, every_attr)) + " "

        str_repr += "bids - ["
        for b in self.bid:
            str_repr += "\n" + str(b)
        str_repr += "] "

        str_repr += "asks - ["
        for a in self.ask:
            str_repr += "\n" + str(a)
        str_repr += "]"

        str_repr += "]"

        return str_repr

    @classmethod
    def from_poloniex(cls, json_document, currency, timest):
        """
        {"asks":[["0.00006604",11590.35669799],["0.00006606",25756.70896058]],
        "bids":[["0.00006600",46771.47390146],["0.00006591",25268.665],],
        "isFrozen":"0","seq":41049600}
        """
        timest = timest
        pair_id = get_currency_pair_from_poloniex(currency)

        sell_bids = []
        for b in json_document["asks"]:
            sell_bids.append(Deal(b[0], b[1]))

        buy_bids = []
        for b in json_document["bids"]:
            buy_bids.append(Deal(b[0], b[1]))

        sequence_id = long(json_document["seq"])

        return OrderBook(pair_id, timest, sell_bids, buy_bids, EXCHANGE.POLONIEX, sequence_id)

    @classmethod
    def from_kraken(cls, json_document, currency, timest):
        """
        {"error":[],"result":{"XETHXXBT":{"asks":[["0.081451","0.200",1501690777],["0.081496","163.150",1501691124]
        "bids":[["0.080928","0.100",1501691107],["0.080926","0.255",1501691110]
        """

        sell_bids = []
        for b in json_document["asks"]:
            sell_bids.append(Deal(b[0], b[1]))

        buy_bids = []
        for b in json_document["bids"]:
            buy_bids.append(Deal(b[0], b[1]))

        pair_id = get_currency_pair_from_kraken(currency)

        return OrderBook(pair_id, timest, sell_bids, buy_bids, EXCHANGE.KRAKEN)

    @classmethod
    def from_bittrex(cls, json_document, currency, timest):
        """
        {"success":true,"message":"","result":{"buy":[{"Quantity":12.76073322,"Rate":0.01557999},{"Quantity":12.01802925,"Rate":0.01557998}
        "sell":[{"Quantity":0.38767680,"Rate":0.01560999},{"Quantity":2.24182363,"Rate":0.01561999}
        """

        sell_bids = []
        if "sell" in json_document and json_document["sell"] is not None:
            for b in json_document["sell"]:
                sell_bids.append(Deal(b["Rate"], b["Quantity"]))

        buy_bids = []
        if "buy" in json_document and json_document["buy"] is not None:
            for b in json_document["buy"]:
                buy_bids.append(Deal(b["Rate"], b["Quantity"]))

        pair_id = get_currency_pair_from_bittrex(currency)

        return OrderBook(pair_id, timest, sell_bids, buy_bids, EXCHANGE.BITTREX)

    @classmethod
    def from_binance(cls, json_document, currency, timest):
        """
        "lastUpdateId":1668114,"bids":[["0.40303000","22.00000000",[]],],"asks":[["0.41287000","1.00000000",[]]
        """

        sell_bids = []
        if "asks" in json_document:
            for b in json_document["asks"]:
                sell_bids.append(Deal(price=b[0], volume=b[1]))

        buy_bids = []
        if "bids" in json_document:
            for b in json_document["bids"]:
                buy_bids.append(Deal(price=b[0], volume=b[1]))

        pair_id = get_currency_pair_from_binance(currency)

        sequence_id = long(json_document["lastUpdateId"])

        return OrderBook(pair_id, timest, sell_bids, buy_bids, EXCHANGE.BINANCE, sequence_id)

    @classmethod
    def from_huobi(cls, json_document, pair_name, timest):
        """
        "tick": {
            "id": 1489464585407,
            "ts": 1489464585407,
            "bids": [
              [7964, 0.0678], // [price, amount]
              [7963, 0.9162],
              [7961, 0.1],
            ],
            "asks": [
              [7979, 0.0736],
              [7980, 1.0292],
            ]

        :param pair_name:
        :param timest:
        :return:
        """

        sell_bids = []
        if "asks" in json_document:
            for b in json_document["asks"]:
                sell_bids.append(Deal(price=b[0], volume=b[1]))

        buy_bids = []
        if "bids" in json_document:
            for b in json_document["bids"]:
                buy_bids.append(Deal(price=b[0], volume=b[1]))

        pair_id = get_currency_pair_from_huobi(pair_name)

        sequence_id = long(json_document["version"])

        return OrderBook(pair_id, timest, sell_bids, buy_bids, EXCHANGE.HUOBI, sequence_id)

    @classmethod
    def from_string(cls, some_string):
        # [exchange - KRAKEN exchange_id - 2 pair - BTC_TO_XRP pair_id - 4 timest - 1502466918
        # bids - [[price - 5.055e-05 volume - 2595.354 ][price - 5.054e-05 volume - 70162.004 ]] asks - [[]]
        results = regex.findall(some_string)

        exchange_id = results[0][1]
        currency_pair_id = results[0][3]
        timest = results[0][4]

        ask_bids = cls.parse_array_deals(results[0][6])
        sell_bids = cls.parse_array_deals(results[0][5])

        return OrderBook(currency_pair_id, timest, ask_bids, sell_bids, exchange_id)

    @classmethod
    def parse_array_deals(cls, some_string):
        res = []

        deals = deal_array_regex.findall(some_string)

        for pair in deals:
            res.append(Deal(pair[0], pair[1]))

        return res

    @classmethod
    def from_row(cls, db_row, asks_rows, sell_rows):
        # id, pair_id, exchange_id, timest, date_time
        # id, order_book_id, price, volume

        currency_pair_id = db_row[1]
        exchange_id = db_row[2]
        timest = db_row[3]

        ask_bids = []
        for r in asks_rows:
            ask_bids.append(Deal(r[2], r[3]))

        sell_bids = []
        for r in sell_rows:
            sell_bids.append(Deal(r[2], r[3]))

        return OrderBook(currency_pair_id, timest, ask_bids, sell_bids, exchange_id)

    def insert_new_bid_preserve_order(self, bid):
        """

        Bids array are sorted in reversed order i.e. highest - first
        NOTE: consider new value volume as overwrite

        :param bid:
        :return:
        """

        almost_zero = bid.volume <= MAX_VOLUME_ORDER_BOOK
        item_insert_point = binary_search(self.bid, bid, cmp_method_bid)
        is_present = False
        if item_insert_point < len(self.bid):
            is_present = self.bid[item_insert_point] == bid
        should_delete = almost_zero and is_present

        if should_delete:
            del self.bid[item_insert_point]
        elif is_present:
            self.bid[item_insert_point].volume = bid.volume
        elif not almost_zero:
            # FIXME NOTE O(n) - slow by python implementation
            self.bid.insert(item_insert_point, bid)

    def insert_new_ask_preserve_order(self, new_ask):
        """
        Ask array are sorted in reversed order i.e. lowest - first

        self.ask = sorted(self.ask, key = lambda x: x.price, reverse=False)

        :param new_ask:
        :return:
        """

        almost_zero = new_ask.volume <= MAX_VOLUME_ORDER_BOOK
        item_insert_point = binary_search(self.ask, new_ask, cmp_method_ask)
        is_present = False
        if item_insert_point < len(self.ask):
            is_present = self.ask[item_insert_point] == new_ask
        should_delete = almost_zero and is_present

        if should_delete:
            del self.ask[item_insert_point]
        elif is_present:
            self.ask[item_insert_point].volume = new_ask.volume
        elif not almost_zero:
            # FIXME NOTE O(n) - slow by python implementation
            self.ask.insert(item_insert_point, new_ask)

    def update_for_poloniex(self, order_book_delta):
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

        [24,219199090,[["o",1,"0.04122908","0.01636493"],["t","10026908",0,"0.04122908","0.00105314",1527880700]]]
        [24,219201009,[["o",0,"0.04111587","0.00000000"],["o",0,"0.04111174","1.52701255"]]]
        [24,219164304,[["o",1,"0.04064791","0.01435233"],["o",1,"0.04068034","0.16858384"]]]
        :param order_book_delta:
        :return:
        """

        # FIXME NOTE sequence number

        POLONIEX_ORDER = "o"
        POLONIEX_TRADE = "t"

        POLONIEX_ORDER_BID = 1
        POLONIEX_ORDER_ASK = 0

        # We suppose that bid and ask are sorted in particular order:
        # for bids - highest - first
        # for asks - lowest - first
        if len(order_book_delta) < 3:
            return

        delta = order_book_delta[2]
        for entry in delta:
            if entry[0] == POLONIEX_ORDER:
                new_deal = Deal(entry[2], entry[3])

                # If it is just orders - we insert in a way to keep sorted order
                if entry[1] == POLONIEX_ORDER_ASK:
                    self.insert_new_ask_preserve_order(new_deal)
                elif entry[1] == POLONIEX_ORDER_BID:
                    self.insert_new_bid_preserve_order(new_deal)
                else:
                    msg = "Poloniex socket update parsing - {wtf} total: {ttt}".format(wtf=entry, ttt=order_book_delta)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            elif entry[0] == POLONIEX_TRADE:

                # FIXME NOTE:   this is ugly hack to avoid creation of custom objects
                #               and at the same Deal object contains lt method that
                #               used by bisect for efficient binary search in sorted list
                new_deal = Deal(entry[3], entry[4])

                # For trade - vice-versa we should update opposite arrays:
                # in case we have trade with type bid -> we will update orders at ask
                # in case we have trade with type ask -> we will update orders at bid

                if entry[2] == POLONIEX_ORDER_BID:

                    item_insert_point = binary_search(self.ask, new_deal, cmp_method_ask)
                    is_present = self.ask[item_insert_point] == new_deal

                    if is_present:
                        self.ask[item_insert_point].volume -= new_deal.volume
                        if self.ask[item_insert_point].volume <= MAX_VOLUME_ORDER_BOOK:
                            del self.ask[item_insert_point]
                    else:
                        msg = "Poloniex socket update we got trade but cant find order price for it: {wtf}".format(
                            wtf=new_deal)
                        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

                elif entry[2] == POLONIEX_ORDER_ASK:

                    item_insert_point = binary_search(self.bid, new_deal, cmp_method_bid)
                    is_present = self.bid[item_insert_point] == new_deal
                    if is_present:
                        self.bid[item_insert_point].volume -= new_deal.volume
                        if self.bid[item_insert_point].volume <= MAX_VOLUME_ORDER_BOOK:
                            del self.bid[item_insert_point]
                    else:
                        msg = "Poloniex socket update we got trade but cant find order price for it: {wtf}".format(
                            wtf=new_deal)
                        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                else:
                    msg = "Poloniex socket update parsing - {wtf}".format(wtf=entry)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            else:
                msg = "Poloniex socket update parsing - UNKNOWN TYPE - {wtf}".format(wtf=entry)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    def update_for_bittrex(self, order_book_delta):
        """
        https://bittrex.github.io/#callback-for-1
        "S" = "Sells"
        "Z" = "Buys"

        "Q" = "Quantity"
        "R" = "Rate"
        "TY" = "Type"
        The Type key can be one of the following values: 0 = ADD, 1 = REMOVE, 2 = UPDATE

        "M" = "MarketName"
        "N" = "Nonce"

        "f" = "Fills"

        3 {u'S': [],
        u'Z': [{u'Q': 0.0, u'R': 0.04040231, u'TY': 1}, {u'Q': 0.78946119, u'R': 0.00126352, u'TY': 0}],
        u'M': u'BTC-DASH',
        u'f': [],
        u'N': 15692}

        3 {u'S': [],
        u'Z': [{u'Q': 1.59914865, u'R': 0.040436, u'TY': 0}, {u'Q': 0.0, u'R': 0.04040232, u'TY': 1}],
        u'M': u'BTC-DASH',
        u'f': [],
        u'N': 15691}


        u'f': [
            {u'Q': 0.11299437,
            u'R': 0.042135,
            u'OT': u'BUY',
            u'T': 1527961548500},
            {u'Q': 0.39487459, u'R': 0.04213499, u'OT': u'BUY', u'T': 1527961548500}],

        :param order_book_delta:
        :return:
        """

        sells = order_book_delta["S"]
        buys = order_book_delta["Z"]
        fills = order_book_delta["f"]

        BITTREX_ORDER_ADD = 0
        BITTREX_ORDER_REMOVE = 1
        BITTREX_ORDER_UPDATE = 2

        for new_sell in sells:

            new_deal = Deal(new_sell["R"], new_sell["Q"])

            if "TY" not in new_sell:
                msg = "Bittrex socket update - within SELL array some weird format - no TY - {wtf}".format(
                    wtf=new_sell)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                continue

            type_update = int(new_sell["TY"])

            item_insert_point = binary_search(self.ask, new_deal, cmp_method_ask)
            is_present = False

            if item_insert_point < len(self.ask):
                is_present = self.ask[item_insert_point] == new_deal
            else:
                msg = "for item {wtf} SELL - ASK found index is {idx}".format(wtf=new_deal, idx=item_insert_point)
                log_to_file(msg, "fuck.log")
                log_to_file(self, "fuck.log")

            if type_update == BITTREX_ORDER_ADD:
                self.insert_new_ask_preserve_order(new_deal)
            elif type_update == BITTREX_ORDER_REMOVE:
                if is_present:
                    del self.ask[item_insert_point]
                else:
                    msg = "Bittrex socket update - got sell REMOVE not found in local orderbook - {wtf}".format(wtf=new_sell)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            elif type_update == BITTREX_ORDER_UPDATE:
                if is_present:
                    self.ask[item_insert_point].volume = new_deal.volume
                else:
                    self.insert_new_ask_preserve_order(new_deal)
            else:
                msg = "Bittrex socket un-supported sells format? {wtf}".format(wtf=new_sell)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        for new_buy in buys:

            new_deal = Deal(new_buy["R"], new_buy["Q"])

            if "TY" not in new_buy:
                msg = "Bittrex socket update - within BUYS array some weird format - no TY - {wtf}".format(wtf=new_buy)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
                continue

            type_update = int(new_buy["TY"])

            item_insert_point = binary_search(self.bid, new_deal, cmp_method_bid)

            is_present = False

            if item_insert_point < len(self.bid):
                is_present = self.bid[item_insert_point] == new_deal
            else:
                msg = "for {wtf} BUY - BID we found index {idx}".format(wtf=new_deal, idx=item_insert_point)
                log_to_file(msg, "fuck.log")
                log_to_file(self, "fuck.log")

            if type_update == BITTREX_ORDER_ADD:
                self.insert_new_bid_preserve_order(new_deal)
            elif type_update == BITTREX_ORDER_REMOVE:
                if is_present:
                    del self.bid[item_insert_point]
                else:
                    msg = "Bittrex socket update - got buy REMOVE not found in local orderbook - {wtf}".format(
                        wtf=new_buy)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            elif type_update == BITTREX_ORDER_UPDATE:
                if is_present:
                    self.bid[item_insert_point].volume = new_deal.volume
                else:
                    self.insert_new_bid_preserve_order(new_deal)
            else:
                msg = "Bittrex socket un-supported buys format? {wtf}".format(wtf=new_buy)
                log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        for new_fill in fills:
            new_deal = Deal(new_fill["R"], new_fill["Q"])

            if "TY" in new_fill:
                msg = "Bittrex socket update - within FILLS array some weird format - no TY - {wtf}".format(wtf=new_fill)
                log_to_file(msg, "should_not_see_you.log")
                continue

            deal_direction = DEAL_TYPE.BUY if "BUY" in new_fill["OT"] else DEAL_TYPE.SELL

            if deal_direction == DEAL_TYPE.BUY:

                item_insert_point = binary_search(self.bid, new_deal, cmp_method_bid)
                is_present = self.bid[item_insert_point] == new_deal

                if is_present:
                    self.bid[item_insert_point].volume -= new_deal.volume
                    if self.bid[item_insert_point].volume <= FLOAT_POINT_PRECISION:
                        del self.bid[item_insert_point]
                else:
                    msg = "Bittrex socket CANT FIND fill request FILL AND UPDATE - BUY??? {wtf}".format(wtf=new_deal)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
            else:
                item_insert_point = binary_search(self.ask, new_deal, cmp_method_ask)
                is_present = self.bid[item_insert_point] == new_deal

                if is_present:
                    self.ask[item_insert_point].volume -= new_deal.volume
                    if self.ask[item_insert_point].volume <= FLOAT_POINT_PRECISION:
                        del self.ask[item_insert_point]
                    else:
                        msg = "Bittrex socket CANT FIND fill request FILL AND UPDATE - SELL??? {wtf}".format(wtf=new_deal)
                        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    def update_for_binance(self, order_book_delta):
        """

        How to manage a local order book correctly
        Open a stream to wss://stream.binance.com:9443/ws/bnbbtc@depth
        Buffer the events you receive from the stream
        Get a depth snapshot from **https://www.binance.com/api/v1/depth?symbol=BNBBTC&limit=1000"
        Drop any event where u is <= lastUpdateId in the snapshot
        The first processed should have U <= lastUpdateId+1 AND u >= lastUpdateId+1
        While listening to the stream, each new event's U should be equal to the previous event's u+1
        The data in each event is the absolute quantity for a price level
        If the quantity is 0, remove the price level
        Receiving an event that removes a price level that is not in your local order book can happen and is normal.

        4
        {"e": "depthUpdate", "E": 1527861613915, "s": "DASHBTC", "U": 45790140, "u": 45790142,
         "b": [["0.04073500", "2.02000000", []], ["0.04073200", "0.00000000", []]],
         "a": [["0.04085300", "0.00000000", []]]}

        :param order_book_delta:
        :return:
        """

        # FIXME NOTE - id ???

        asks = order_book_delta["a"]
        bids = order_book_delta["b"]

        for a in asks:
            new_deal = Deal(a[0], a[1])
            if new_deal.volume > 0:
                self.insert_new_ask_preserve_order(new_deal)
            else:

                item_insert_point = binary_search(self.ask, new_deal, cmp_method_ask)
                is_present = self.ask[item_insert_point] == new_deal

                if is_present:
                    del self.ask[item_insert_point]
                else:
                    msg = "BINANCE socket CANT FIND IN ASK update {wtf}".format(wtf=new_deal)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        for a in bids:
            new_deal = Deal(a[0], a[1])

            if new_deal.volume > 0:
                self.insert_new_bid_preserve_order(new_deal)
            else:

                item_insert_point = binary_search(self.bid, new_deal, cmp_method_bid)
                is_present = self.bid[item_insert_point] == new_deal

                if is_present:
                    del self.bid[item_insert_point]
                else:
                    msg = "BINANCE socket CANT FIND IN BID update {wtf}".format(wtf=new_deal)
                    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

    def update_for_huobi(self, order_book_delta):
        if "tick" in order_book_delta:
            import copy
            from utils.time_utils import get_now_seconds_utc

            pair_name = get_currency_pair_to_huobi(self.pair_id)

            order_book2 = OrderBook.from_huobi(order_book_delta["tick"], pair_name, get_now_seconds_utc())

            # FIXME NOTE - anything else except bid\ask ???

            self.ask = copy.deepcopy(order_book2.ask)
            self.bid = copy.deepcopy(order_book2.bid)

            self.sort_by_price()

        else:
            print "update for huobi: ", order_book_delta

    def update(self, exchange_id, order_book_delta):

        ts = str(get_now_seconds_utc_ms())
        e_name = get_exchange_name_by_id(exchange_id)
        
        file_name = e_name + "_" + ts + "_raw.txt" 
        log_to_file(order_book_delta, file_name)
        
        file_name = e_name + "_" + ts + "_before.txt"
        log_to_file(self, file_name)

        method = {
            EXCHANGE.POLONIEX: self.update_for_poloniex,
            EXCHANGE.BITTREX: self.update_for_bittrex,
            EXCHANGE.BINANCE: self.update_for_binance,
            EXCHANGE.HUOBI: self.update_for_huobi
        }[exchange_id]
        method(order_book_delta)

        file_name = e_name + "_" + ts + "_after.txt"
        log_to_file(self, file_name)
       
