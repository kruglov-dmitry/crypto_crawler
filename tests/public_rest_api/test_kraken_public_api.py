import unittest

from data.ticker import Ticker
from data.candle import Candle
from data.order_book import OrderBook
from data.trade_history import TradeHistory

from utils.time_utils import get_now_seconds_local, get_now_seconds_utc
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from kraken.ticker_utils import get_ticker_kraken
from kraken.ohlc_utils import get_ohlc_kraken
from kraken.order_book_utils import get_order_book_kraken
from kraken.history_utils import get_history_kraken
from kraken.constants import KRAKEN_CURRENCIES


class KrakenPublicApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)

    def test_kraken_ticker_retrieval(self):
        timest = get_now_seconds_local()
        for pair_name in KRAKEN_CURRENCIES:
            ticker = get_ticker_kraken(pair_name, timest)
            if ticker:
                self.assertEquals(type(ticker), Ticker)

    def test_kraken_ohlc_retrieval(self):
        date_end = get_now_seconds_utc()
        date_start = date_end - 900
        for pair_name in KRAKEN_CURRENCIES:
            period = 15
            candles = get_ohlc_kraken(pair_name, date_start, date_end, period)
            for candle in candles:
                if candle:
                    self.assertEquals(type(candle), Candle)

    def test_kraken_order_book_retrieval(self):
        timest = get_now_seconds_utc()
        for currency in KRAKEN_CURRENCIES:
            order_book = get_order_book_kraken(currency, timest)
            if order_book:
                self.assertEquals(type(order_book), OrderBook)

    def test_kraken_trade_history_retrieval(self):
        today = get_now_seconds_utc()
        yesterday = today - 24 * 3600
        for pair_name in KRAKEN_CURRENCIES:
            trade_history = get_history_kraken(pair_name, yesterday, today)
            for entry in trade_history:
                if entry:
                    self.assertEquals(type(entry), TradeHistory)
