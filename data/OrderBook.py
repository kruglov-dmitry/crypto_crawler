import re
from utils.currency_utils import get_pair_name_by_id

from bittrex.currency_utils import get_currency_pair_from_bittrex
from kraken.currency_utils import get_currency_pair_from_kraken
from poloniex.currency_utils import get_currency_pair_from_poloniex
from binance.currency_utils import get_currency_pair_from_binance

from BaseData import BaseData
from Deal import Deal
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import get_date_time_from_epoch

# FIXME NOTE - not the smartest idea to deal with
regex_string = "\[exchange - (.*) exchange_id - (.*) pair - (.*) pair_id - (.*) timest - (.*) bids - (.*) asks - (.*)\]"
regex = re.compile(regex_string)

deal_array_regex_string = "price - ([0-9]*.[0-9e-]*) volume - ([0-9]*.[0-9e-]*)"
deal_array_regex = re.compile(deal_array_regex_string)

ORDER_BOOK_INSERT_QUERY = "insert into order_book(pair_id, exchange_id, timest, date_time) " \
                          "values(%s, %s, %s, %s) RETURNING id;"
ORDER_BOOK_TYPE_NAME = "order_book"

ORDER_BOOK_INSERT_BIDS = "insert into order_book_bid(order_book_id, price, volume) values (%s, %s, %s);"
ORDER_BOOK_INSERT_ASKS = "insert into order_book_ask(order_book_id, price, volume) values (%s, %s, %s);"


class OrderBook(BaseData):
    insert_query = ORDER_BOOK_INSERT_QUERY
    type = ORDER_BOOK_TYPE_NAME

    def __init__(self, pair_id, timest, ask_bids, sell_bids, exchange_id):
        # FIXME NOTE - various volume data?
        self.pair_id = int(pair_id)
        self.pair = get_pair_name_by_id(self.pair_id)
        self.timest = timest
        self.ask = ask_bids
        self.bid = sell_bids
        self.exchange_id = int(exchange_id)
        self.exchange = get_exchange_name_by_id(self.exchange_id)

    def sort_by_price(self):
        self.bid = sorted(self.bid, key=lambda x: x.price, reverse=True)        # highest - first
        self.ask = sorted(self.ask, key = lambda x: x.price, reverse=False)     # lowest - first

    def trim_highest_bid_and_lowest_ask(self):
        self.bid = self.bid[1:]
        self.ask = self.ask[:-1]

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
            str_repr += str(b)
        str_repr += "] "

        str_repr += "asks - ["
        for a in self.ask:
            str_repr += str(a)
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
        currency_pair = get_currency_pair_from_poloniex(currency)

        ask_bids = []
        for b in json_document["asks"]:
            ask_bids.append(Deal(b[0], b[1]))

        sell_bids = []
        for b in json_document["bids"]:
            sell_bids.append(Deal(b[0], b[1]))

        return OrderBook(currency_pair, timest, ask_bids, sell_bids, EXCHANGE.POLONIEX)

    @classmethod
    def from_kraken(cls, json_document, currency, timest):
        """
        {"error":[],"result":{"XETHXXBT":{"asks":[["0.081451","0.200",1501690777],["0.081496","163.150",1501691124]
        "bids":[["0.080928","0.100",1501691107],["0.080926","0.255",1501691110]
        """

        ask_bids = []
        for b in json_document["asks"]:
            ask_bids.append(Deal(b[0], b[1]))

        sell_bids = []
        for b in json_document["bids"]:
            sell_bids.append(Deal(b[0], b[1]))

        currency_pair = get_currency_pair_from_kraken(currency)

        return OrderBook(currency_pair, timest, ask_bids, sell_bids, EXCHANGE.KRAKEN)

    @classmethod
    def from_bittrex(cls, json_document, currency, timest):
        """
        {"success":true,"message":"","result":{"buy":[{"Quantity":12.76073322,"Rate":0.01557999},{"Quantity":12.01802925,"Rate":0.01557998}
        "sell":[{"Quantity":0.38767680,"Rate":0.01560999},{"Quantity":2.24182363,"Rate":0.01561999}
        """

        ask_bids = []
        if "sell" in json_document:
            for b in json_document["sell"]:
                ask_bids.append(Deal(b["Rate"], b["Quantity"]))

        sell_bids = []
        if "buy" in json_document:
            for b in json_document["buy"]:
                sell_bids.append(Deal(b["Rate"], b["Quantity"]))

        currency_pair = get_currency_pair_from_bittrex(currency)

        return OrderBook(currency_pair, timest, ask_bids, sell_bids, EXCHANGE.BITTREX)

    @classmethod
    def from_binance(cls, json_document, currency, timest):
        """
        "lastUpdateId":1668114,"bids":[["0.40303000","22.00000000",[]],],"asks":[["0.41287000","1.00000000",[]]
        """

        ask_bids = []
        if "asks" in json_document:
            for b in json_document["asks"]:
                ask_bids.append(Deal(price=b[0], volume=b[1]))

        sell_bids = []
        if "bids" in json_document:
            for b in json_document["bids"]:
                sell_bids.append(Deal(price=b[0], volume=b[1]))

        currency_pair = get_currency_pair_from_binance(currency)

        return OrderBook(currency_pair, timest, ask_bids, sell_bids, EXCHANGE.BINANCE)

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
