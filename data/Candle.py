from datetime import datetime
import re

from utils.currency_utils import get_pair_name_by_id, get_currency_pair_from_bittrex, \
    get_currency_pair_from_kraken, get_currency_pair_from_poloniex

from BaseData import BaseData
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import get_date_time_from_epoch

# FIXME NOTE - not the smartest idea to deal with
regex_string = "\[close - (.*) exchange - (.*) exchange_id - (.*) high - (.*) low - (.*) open - (.*) pair - (.*) pair_id - (.*) timest - (.*)\]"
regex = re.compile(regex_string)

CANDLE_INSERT_QUERY = "insert into candle (pair_id, exchange_id, open, close, high, low, timest, date_time)" \
                      " values (%s, %s, %s, %s, %s, %s, %s, %s);"
CANDLE_TYPE_NAME = "ohlc"

class Candle(BaseData):
    insert_query = CANDLE_INSERT_QUERY
    type = CANDLE_TYPE_NAME

    def __init__(self, pair_id, timest, price_high, price_low, price_open, price_close, exchange_id):
        # FIXME NOTE - various volume data?
        self.pair_id = pair_id
        self.pair = get_pair_name_by_id(pair_id)
        self.timest = long(timest)
        self.high = float(price_high)
        self.low = float(price_low)
        self.open = float(price_open)
        self.close = float(price_close)
        self.exchange_id = exchange_id
        self.exchange = get_exchange_name_by_id(exchange_id)

    def get_pg_arg_list(self):
        return (self.pair_id,
                self.exchange_id,
                self.open,
                self.close,
                self.high,
                self.low,
                self.timest,
                get_date_time_from_epoch(self.timest)
                )

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

    @classmethod
    def from_string(cls, some_string):
        #[close - 0.07019143 exchange - BITTREX exchange_id - 3 high - 0.07031782 low - 0.06912551 open - 0.06912551
        # pair - BTC_TO_DASH pair_id - 1 timest - 1499000400]
        results = regex.findall(some_string)

        # [('0.07019143', 'BITTREX', '3', '0.07031782', '0.06912551', '0.06912551', 'BTC_TO_DASH', '1', '1499000400')]
        price_close = results[0][0]
        exchange_id = results[0][2]
        price_high = results[0][3]
        price_low = results[0][4]
        price_open = results[0][5]
        currency_pair_id = results[0][7]
        timest = results[0][8]

        return Candle(currency_pair_id, timest, price_high, price_low, price_open, price_close, exchange_id)