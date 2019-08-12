import unittest

from data.ticker import Ticker
from data.candle import Candle
from data.order_book import OrderBook
from data.trade_history import TradeHistory

from utils.time_utils import get_now_seconds_local, get_now_seconds_utc
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from bittrex.ticker_utils import get_ticker_bittrex
from bittrex.ohlc_utils import get_ohlc_bittrex
from bittrex.order_book_utils import get_order_book_bittrex
from bittrex.history_utils import get_history_bittrex
from bittrex.constants import BITTREX_CURRENCY_PAIRS


class BittrexPublicApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)

    def test_bittrex_ticker_retrieval(self):
        timest = get_now_seconds_local()
        for pair_name in BITTREX_CURRENCY_PAIRS:
            ticker = get_ticker_bittrex(pair_name, timest)
            if ticker:
                self.assertEquals(type(ticker), Ticker)

    def test_bittrex_ohlc_retrieval(self):
        date_end = get_now_seconds_utc()
        date_start = date_end - 900
        for pair_name in BITTREX_CURRENCY_PAIRS:
            period = "thirtyMin"
            candles = get_ohlc_bittrex(pair_name, date_start, date_end, period)
            for candle in candles:
                if candle:
                    self.assertEquals(type(candle), Candle)

    def test_bittrex_order_book_retrieval(self):
        timest = get_now_seconds_utc()
        for currency in BITTREX_CURRENCY_PAIRS:
            order_book = get_order_book_bittrex(currency, timest)
            if order_book:
                self.assertEquals(type(order_book), OrderBook)

    def test_bittrex_trade_history_retrieval(self):
        today = get_now_seconds_utc()
        yesterday = today - 24 * 3600
        for pair_name in BITTREX_CURRENCY_PAIRS:
            trade_history = get_history_bittrex(pair_name, yesterday, today)
            for entry in trade_history:
                if entry:
                    self.assertEquals(type(entry), TradeHistory)
