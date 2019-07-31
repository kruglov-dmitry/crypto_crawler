from datetime import datetime
import re
from decimal import Decimal

from utils.currency_utils import get_pair_name_by_id

from bittrex.currency_utils import get_currency_pair_from_bittrex
from kraken.currency_utils import get_currency_pair_from_kraken
from poloniex.currency_utils import get_currency_pair_from_poloniex
from binance.currency_utils import get_currency_pair_from_binance
from huobi.currency_utils import get_currency_pair_from_huobi

from data.base_data import BaseData
from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import get_date_time_from_epoch

# FIXME NOTE - not the smartest idea to deal with
regex_string = "\[amount - (.*) deal_type - (.*) exchange - (.*) exchange_id - (.*) pair - (.*) pair_id - (.*) price - (.*) timest - (.*) total - (.*)\]"
regex = re.compile(regex_string)


TRADE_HISTORY_TABLE_NAME = "trade_history"
TRADE_HISTORY_COLUMNS = ("pair_id", "exchange_id", "deal_type", "price", "amount", "total", "timest", "date_time")
TRADE_HISTORY_INSERT_QUERY = "insert into {table_name} ({columns}) values(%s, %s, %s, %s, %s, %s, %s, %s);".format(
    table_name=TRADE_HISTORY_TABLE_NAME, columns=','.join(TRADE_HISTORY_COLUMNS))
TRADE_HISTORY_TYPE_NAME = "trade_history"


class TradeHistory(BaseData):
    insert_query = TRADE_HISTORY_INSERT_QUERY
    type = TRADE_HISTORY_TYPE_NAME

    table_name = TRADE_HISTORY_TABLE_NAME
    columns = TRADE_HISTORY_COLUMNS

    def __init__(self, pair_id, timest, deal_type, price, amount, total, exchange_id):
        # FIXME NOTE - various volume data?
        self.pair_id = int(pair_id)
        self.pair = get_pair_name_by_id(self.pair_id)
        self.timest = long(timest)
        self.deal_type = deal_type
        self.price = Decimal(price)
        self.amount = Decimal(amount)
        self.total = Decimal(total)
        self.exchange_id = int(exchange_id)
        self.exchange = get_exchange_name_by_id(self.exchange_id)

    def tsv(self):
        return ("{}\t{}\t{}\t{}\t{}\t{}\t{}\t'{}'".format(
            self.pair_id, self.exchange_id, self.deal_type, self.price, self.amount, self.total, self.timest,
            get_date_time_from_epoch(self.timest)).decode('utf8'))

    def get_pg_arg_list(self):
        return (self.pair_id,
                self.exchange_id,
                self.deal_type,
                self.price,
                self.amount,
                self.total,
                self.timest,
                get_date_time_from_epoch(self.timest)
                )

    @classmethod
    def from_poloniex(cls, json_document, pair, timest):
        """
        {
          "globalTradeID":202950655,
          "tradeID":2459916,
          "date":"2017-08-02 17:06:09",
          "type":"sell",
          "rate":"0.00006476",
          "amount":"323.78885919",
          "total":"0.02096856"
        }
        """

        utc_time = datetime.strptime(json_document["date"], "%Y-%m-%d %H:%M:%S")
        deal_timest = (utc_time - datetime(1970, 1, 1)).total_seconds()

        deal_type = DEAL_TYPE.BUY

        if "sell" in json_document["type"]:
            deal_type = DEAL_TYPE.SELL

        price = json_document["rate"]
        amount = json_document["amount"]
        total = json_document["total"]

        currency_pair = get_currency_pair_from_poloniex(pair)

        return TradeHistory(currency_pair, deal_timest, deal_type, price, amount, total, EXCHANGE.POLONIEX)

    @classmethod
    def from_kraken(cls, json_document, pair, timest):
        """
        <pair_name> = pair name
            array of array entries(<price>, <volume>, <time>, <buy/sell>, <market/limit>, <miscellaneous>)
        last = id to be used as since when polling for new trade data
        """

        deal_timest = json_document[2]
        deal_type = DEAL_TYPE.BUY

        if "s" in json_document[3]:
            deal_type = DEAL_TYPE.SELL

        price = Decimal(json_document[0])
        amount = Decimal(json_document[1])
        total = price * amount

        currency_pair = get_currency_pair_from_kraken(pair)

        return TradeHistory(currency_pair, deal_timest, deal_type, price, amount, total, EXCHANGE.KRAKEN)


    @classmethod
    def from_bittrex(cls, json_document, pair, timest):
        """
        [
           {
              "Id":59926023,
              "TimeStamp":"2017-08-02T17:11:28.033",
              "Quantity":3.49909364,
              "Price":0.01565000,
              "Total":0.05476081,
              "FillType":"FILL",
              "OrderType":"SELL"
           },
           {
              "Id":59926007,
              "TimeStamp":"2017-08-02T17:11:15.83",
              "Quantity":0.11242970,
              "Price":0.01566000,
              "Total":0.00176064,
              "FillType":"FILL",
              "OrderType":"BUY"
           }
        ]
        """

        try:
            utc_time = datetime.strptime(json_document["TimeStamp"], "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            utc_time = datetime.strptime(json_document["TimeStamp"], "%Y-%m-%dT%H:%M:%S")

        deal_timest = (utc_time - datetime(1970, 1, 1)).total_seconds()

        deal_type = DEAL_TYPE.BUY

        if "SELL" in json_document["OrderType"]:
            deal_type = DEAL_TYPE.SELL

        price = Decimal(json_document["Price"])
        amount = Decimal(json_document["Quantity"])
        total = json_document["Total"]

        currency_pair = get_currency_pair_from_bittrex(pair)

        return TradeHistory(currency_pair, deal_timest, deal_type, price, amount, total, EXCHANGE.BITTREX)

    @classmethod
    def from_binance(cls, json_document, pair, timest):
        """
         {
                "a": 26129,         // Aggregate tradeId
                "p": "0.01633102",  // Price
                "q": "4.70443515",  // Quantity
                "f": 27781,         // First tradeId
                "l": 27781,         // Last tradeId
                "T": 1498793709153, // Timestamp
                "m": true,          // Was the buyer the maker?
                "M": true           // Was the trade the best price match?
              }
        """

        currency_pair = get_currency_pair_from_binance(pair)
        deal_timest = 0.001 * long(json_document["T"])  # Convert to seconds

        deal_type = DEAL_TYPE.BUY
        if json_document["m"] is True:
            deal_type = DEAL_TYPE.SELL

        price = Decimal(json_document["p"])
        amount = Decimal(json_document["q"])
        total = price * amount

        return TradeHistory(currency_pair, deal_timest, deal_type, price, amount, total, EXCHANGE.BINANCE)

    @classmethod
    def from_huobi(cls, json_document, pair_name, timest):
        """
            {
                "status": "ok",
                "ch": "market.ethusdt.trade.detail",
                "ts": 1502448925216,
                "data": [
                    {
                        "id": 31459998,
                        "ts": 1502448920106,
                        "data": [
                            {
                                "id": 17592256642623,
                                "amount": 0.04,
                                "price": 1997,
                                "direction": "buy",
                                "ts": 1502448920106
                            }
                        ]
                    }
                ]
            }
        :param json_document:
        :param pair_name:
        :param timest:
        :return:
        """

        currency_pair = get_currency_pair_from_huobi(pair_name)
        deal_timest = 0.001 * long(json_document["ts"])  # Convert to seconds

        deal_type = DEAL_TYPE.BUY
        if "buy" not in json_document["direction"]:
            deal_type = DEAL_TYPE.SELL

        price = Decimal(json_document["price"])
        amount = Decimal(json_document["amount"])
        total = price * amount

        return TradeHistory(currency_pair, deal_timest, deal_type, price, amount, total, EXCHANGE.BINANCE)

    @classmethod
    def from_string(cls, some_string):
        # [amount - 0.2288709 deal_type - 2 exchange - POLONIEX exchange_id - 1 pair - BTC_TO_DASH pair_id - 1 price - 0.060019 timest - 1502434895 total - 0 ]
        results = regex.findall(some_string)

        # [('0.2288709', '2', 'POLONIEX', '1', 'BTC_TO_DASH', '1', '0.060019', '1502434895', '0 ')]
        amount = Decimal(results[0][0])
        deal_type = results[0][1]
        exchange_id = results[0][3]
        currency_pair_id = results[0][5]
        price = Decimal(results[0][6])
        deal_timest = results[0][7]
        total = price * amount

        return TradeHistory(currency_pair_id, deal_timest, deal_type, price, amount, total, exchange_id)

    @classmethod
    def from_row(cls, db_row):
        #  id, pair_id, exchange_id, deal_type, price, amount, total, timest, date_time

        currency_pair_id = db_row[1]
        exchange_id = db_row[2]
        deal_type = db_row[3]
        price = db_row[4]
        amount = db_row[5]
        total = db_row[6]
        deal_timest = db_row[7]

        return TradeHistory(currency_pair_id, deal_timest, deal_type, price, amount, total, exchange_id)
