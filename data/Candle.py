from datetime import datetime

from currency_utils import get_pair_name_by_id, get_currency_pair_from_bittrex, \
    get_currency_pair_from_kraken, get_currency_pair_from_poloniex

from BaseData import BaseData
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id


class Candle(BaseData):
    def __init__(self, pair, timest, price_high, price_low, price_open, price_close, exchange):
        # FIXME NOTE - various volume data?
        self.pair_id = pair
        self.pair = get_pair_name_by_id(pair)
        self.timest = long(timest)
        self.high = float(price_high)
        self.low = float(price_low)
        self.open = float(price_open)
        self.close = float(price_close)
        self.exchange_id = exchange
        self.exchange = get_exchange_name_by_id(exchange)

    @classmethod
    def from_poloniex(cls, json_document, currency):
        # {"date":1405699200,"high":0.0045388,"low":0.00403001,"open":0.00404545,"close":0.00435873,"volume":44.34555992,"quoteVolume":10311.88079097,"weightedAverage":0.00430043}
        timest = json_document["date"]
        price_high = json_document["high"]
        price_low = json_document["low"]
        price_open = json_document["open"]
        price_close = json_document["close"]

        currency_pair = get_currency_pair_from_poloniex(currency)

        return Candle(currency_pair, timest, price_high, price_low, price_open, price_close, EXCHANGE.POLONIEX)

    @classmethod
    def from_kraken(cls, json_document, currency):
        # <time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>
        timest = json_document[0]
        price_high = json_document[2]
        price_low = json_document[3]
        price_open = json_document[1]
        price_close = json_document[4]

        currency_pair = get_currency_pair_from_kraken(currency)

        return Candle(currency_pair, timest, price_high, price_low, price_open, price_close, EXCHANGE.KRAKEN)

    @classmethod
    def from_bittrex(cls, json_document, currency):
        """
        result":[
        {"O":0.08184725,"H":0.08184725,"L":0.08181559,"C":0.08181559,"V":9.56201864,"T":"2017-07-21T17:26:00","BV":0.78232812},
        {"O":0.08181559,"H":0.08184725,"L":0.08181559,"C":0.08184725,"V":3.28483907,"T":"2017-07-21T17:27:00","BV":0.26876032}
        FIXME:  ISO 8601-formatted date
        """
        utc_time = datetime.strptime(json_document["T"], "%Y-%m-%dT%H:%M:%S")
        timest = (utc_time - datetime(1970, 1, 1)).total_seconds()
        price_high = json_document["H"]
        price_low = json_document["L"]
        price_open = json_document["O"]
        price_close = json_document["C"]

        currency_pair = get_currency_pair_from_bittrex(currency)

        return Candle(currency_pair, timest, price_high, price_low, price_open, price_close, EXCHANGE.BITTREX)