import re
from decimal import Decimal

from utils.currency_utils import get_pair_name_by_id

from bittrex.currency_utils import get_currency_pair_from_bittrex
from kraken.currency_utils import get_currency_pair_from_kraken
from poloniex.currency_utils import get_currency_pair_from_poloniex
from binance.currency_utils import get_currency_pair_from_binance
from huobi.currency_utils import get_currency_pair_from_huobi

from data.base_data import BaseData
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import get_date_time_from_epoch

# [ask - 0.05828793 bid - 0.057457 exchange - BITTREX exchange_id - 3 pair - BTC_TO_DASH pair_id - 1 timest - 1502466890 ]
# FIXME NOTE - not the smartest idea to deal with
regex_string = "\[ask - (.*) bid - (.*) exchange - (.*) exchange_id - (.*) pair - (.*) pair_id - (.*) timest - (.*)\]"
regex = re.compile(regex_string)

TICKERS_TABLE_NAME = "tickers"
TICKERS_COLUMNS = ("pair_id", "exchange_id", "lowest_ask", "highest_bid", "timest", "date_time")
TICKERS_INSERT_QUERY = """insert into {table_name} ({columns}) values(%s, %s, %s, %s, %s, %s);""".format(
    table_name=TICKERS_TABLE_NAME, columns=','.join(TICKERS_COLUMNS))

TICKER_TYPE_NAME = "ticker"


class Ticker(BaseData):
    insert_query = TICKERS_INSERT_QUERY
    type = TICKER_TYPE_NAME

    table_name = TICKERS_TABLE_NAME
    columns = TICKERS_COLUMNS

    def __init__(self, pair_id, lowest_ask, highest_bid, timest, exchange_id):
        self.pair_id = int(pair_id)
        self.pair = get_pair_name_by_id(self.pair_id)
        self.ask = Decimal(lowest_ask)
        self.bid = Decimal(highest_bid)
        self.timest = long(timest)
        self.exchange_id = int(exchange_id)
        self.exchange = get_exchange_name_by_id(self.exchange_id)

    def tsv(self):
        return ("{}\t{}\t{}\t{}\t{}\t'{}'".format(
            self.pair_id, self.exchange_id, self.ask, self.bid, self.timest,
            get_date_time_from_epoch(self.timest)).decode('utf8'))

    def get_pg_arg_list(self):
        return (self.pair_id,
                self.exchange_id,
                self.ask,
                self.bid,
                self.timest,
                get_date_time_from_epoch(self.timest)
                )

    @classmethod
    def from_poloniex(cls, pair_name, timest, json_document):
        """
        BTC_BCN":{"id": 7, "last": "0.00000047", "lowestAsk": "0.00000048", "highestBid": "0.00000047",
                   "percentChange": "-0.09615384", "baseVolume": "105.01337711", "quoteVolume": "217142084.64192474",
                   "isFrozen": "0", "high24hr": "0.00000052", "low24hr": "0.00000045"}
        """
        lowest_ask = json_document["lowestAsk"]
        highest_bid = json_document["highestBid"]

        currency_pair = get_currency_pair_from_poloniex(pair_name)

        return Ticker(currency_pair, lowest_ask, highest_bid, timest, EXCHANGE.POLONIEX)

    @classmethod
    def from_kraken(cls, pair_name, timest, json_document):
        """{"error":[],"result":{"DASHXBT":
        {"a":["0.06295700","1","1.000"],
        "b":["0.06230800","113","113.000"],
        "c":["0.06295700","9.74800000"],
        "v":["5894.96333766","6925.68918665"],
        "p":["0.06294513","0.06302664"],
        "t":[844,1030],
        "l":["0.06079200","0.06079200"],
        "h":["0.06488000","0.06516300"],
        "o":"0.06210000"}}}

        a = ask array(<price>, <whole lot volume>, <lot volume>),
        b = bid array(<price>, <whole lot volume>, <lot volume>),
        c = last trade closed array(<price>, <lot volume>),
        v = volume array(<today>, <last 24 hours>),
        p = volume weighted average price array(<today>, <last 24 hours>),
        t = number of trades array(<today>, <last 24 hours>),
        l = low array(<today>, <last 24 hours>),
        h = high array(<today>, <last 24 hours>),
        o = today's opening price

        """
        lowest_ask = json_document["a"][0]
        highest_bid = json_document["b"][0]

        currency_pair_id = get_currency_pair_from_kraken(pair_name)

        return Ticker(currency_pair_id, lowest_ask, highest_bid, timest, EXCHANGE.KRAKEN)

    @classmethod
    def from_bittrex(cls, pair_name, timest, json_document):
        """
            {"success":true,"message":"","result":{"Bid":0.01490996,"Ask":0.01491000,"Last":0.01490996}}
        """
        lowest_ask = json_document["Ask"]
        highest_bid = json_document["Bid"]

        currency_pair_id = get_currency_pair_from_bittrex(pair_name)

        return Ticker(currency_pair_id, lowest_ask, highest_bid, timest, EXCHANGE.BITTREX)

    @classmethod
    def from_binance(cls, pair_name, timest, json_document):
        lowest_ask = json_document["askPrice"]
        highest_bid = json_document["bidPrice"]

        currency_pair_id = get_currency_pair_from_binance(pair_name)

        return Ticker(currency_pair_id, lowest_ask, highest_bid, timest, EXCHANGE.BINANCE)

    @classmethod
    def from_huobi(cls, pair_name, timest, json_document):
        """
        {
            "status":"ok",
            "ch":"market.ethusdt.detail.merged",
            "ts":1499225276950,
            "tick":{
              "id":1499225271,
              "ts":1499225271000,
              "close":1885.0000,
              "open":1960.0000,
              "high":1985.0000,
              "low":1856.0000,
              "amount":81486.2926,
              "count":42122,
              "vol":157052744.85708200,
              "ask":[1885.0000,21.8804],
              "bid":[1884.0000,1.6702]
            }
        }

        :return:
        """
        lowest_ask = json_document["ask"][0]
        highest_bid = json_document["bid"][0]

        currency_pair_id = get_currency_pair_from_huobi(pair_name)

        return Ticker(currency_pair_id, lowest_ask, highest_bid, timest, EXCHANGE.HUOBI)

    @classmethod
    def from_string(cls, some_string):
        # [ask - 0.05828793 bid - 0.057457 exchange - BITTREX exchange_id - 3 pair - BTC_TO_DASH pair_id - 1 timest - 1502466890 ]
        results = regex.findall(some_string)

        # [('0.05828793', '0.057457', 'BITTREX', '3', 'BTC_TO_DASH', '1', '1502466890 ')]
        ask = results[0][0]
        bid = results[0][1]
        exchange_id = results[0][3]
        currency_pair_id = results[0][5]
        timest = results[0][6]

        return Ticker(currency_pair_id, ask, bid, timest, exchange_id)

    @classmethod
    def from_row(cls, db_row):
        #  id, exchange_id, pair_id, lowest_ask, highest_bid, timest, date_time

        exchange_id = db_row[1]
        currency_pair_id = db_row[2]
        ask = db_row[3]
        bid = db_row[4]
        timest = db_row[5]

        return Ticker(currency_pair_id, ask, bid, timest, exchange_id)
