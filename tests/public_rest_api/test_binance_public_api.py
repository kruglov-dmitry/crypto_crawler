import unittest

from data.ticker import Ticker
from data.candle import Candle
from data.order_book import OrderBook
from data.trade_history import TradeHistory

from utils.time_utils import get_now_seconds_local, get_now_seconds_utc
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from binance.ticker_utils import get_tickers_binance
from binance.ohlc_utils import get_ohlc_binance
from binance.order_book_utils import get_order_book_binance
from binance.history_utils import get_history_binance
from binance.constants import BINANCE_CURRENCY_PAIRS


class BinancePublicApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)

    def test_binance_ticker_retrieval(self):
        timest = get_now_seconds_local()
        tickers = get_tickers_binance(BINANCE_CURRENCY_PAIRS, timest)
        for ticker in tickers:
            if ticker:
                self.assertEquals(type(ticker), Ticker)

    def test_binance_ohlc_retrieval(self):
        date_end = get_now_seconds_utc()
        date_start = date_end - 900
        for currency in BINANCE_CURRENCY_PAIRS:
            period = "15m"
            candles = get_ohlc_binance(currency, date_start, date_end, period)
            for candle in candles:
                if candle:
                    self.assertEquals(type(candle), Candle)

    def test_binance_order_book_retrieval(self):
        timest = get_now_seconds_utc()
        for currency in BINANCE_CURRENCY_PAIRS:
            order_book = get_order_book_binance(currency, timest)
            if order_book:
                self.assertEquals(type(order_book), OrderBook)

    def test_binance_trade_history_retrieval(self):
        today = get_now_seconds_utc()
        yesterday = today - 24 * 3600
        for pair_name in BINANCE_CURRENCY_PAIRS:
            trade_history = get_history_binance(pair_name, yesterday, today)
            for entry in trade_history:
                if entry:
                    self.assertEquals(type(entry), TradeHistory)
