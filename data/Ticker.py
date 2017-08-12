from currency_utils import get_pair_name_by_id, get_currency_pair_from_bittrex, \
    get_currency_pair_from_kraken, get_currency_pair_from_poloniex

from BaseData import BaseData
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id


class Ticker(BaseData):
    def __init__(self, pair, lowest_ask, highest_bid, timest, exchange):
        self.pair_id = pair
        self.pair = get_pair_name_by_id(pair)
        self.ask = float(lowest_ask)
        self.bid = float(highest_bid)
        self.timest = long(timest)
        self.exchange_id = exchange
        self.exchange = get_exchange_name_by_id(exchange)

    @classmethod
    def from_poloniex(cls, currency, timest, json_document):
        """
        BTC_BCN":{"id": 7, "last": "0.00000047", "lowestAsk": "0.00000048", "highestBid": "0.00000047",
                   "percentChange": "-0.09615384", "baseVolume": "105.01337711", "quoteVolume": "217142084.64192474",
                   "isFrozen": "0", "high24hr": "0.00000052", "low24hr": "0.00000045"}
        """
        lowest_ask = json_document["lowestAsk"]
        highest_bid = json_document["highestBid"]

        currency_pair = get_currency_pair_from_poloniex(currency)

        return Ticker(currency_pair, lowest_ask, highest_bid, timest, EXCHANGE.POLONIEX)

    @classmethod
    def from_kraken(cls, currency, timest, json_document):
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

        currency_pair = get_currency_pair_from_kraken(currency)

        return Ticker(currency_pair, lowest_ask, highest_bid, timest, EXCHANGE.KRAKEN)

    @classmethod
    def from_bittrex(cls, currency, timest, json_document):
        """
            {"success":true,"message":"","result":{"Bid":0.01490996,"Ask":0.01491000,"Last":0.01490996}}
        """
        lowest_ask = json_document["Ask"]
        highest_bid = json_document["Bid"]

        currency_pair = get_currency_pair_from_bittrex(currency)

        return Ticker(currency_pair, lowest_ask, highest_bid, timest, EXCHANGE.BITTREX)