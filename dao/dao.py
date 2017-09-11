from utils.time_utils import get_now_seconds

#
#       FIXME NOTE
#
#   Reconsider imports below
#

from bittrex.constants import BITTREX_CURRENCIES
from kraken.constants import KRAKEN_CURRENCIES
from poloniex.constants import POLONIEX_CURRENCIES

from bittrex.ticker_utils import get_ticker_bittrex
from kraken.ticker_utils import get_ticker_kraken
from poloniex.ticker_utils import get_ticker_poloniex

from bittrex.ohlc_utils import get_ohlc_bittrex
from kraken.ohlc_utils import get_ohlc_kraken
from poloniex.ohlc_utils import get_ohlc_poloniex

from bittrex.order_book_utils import get_order_book_bittrex
from kraken.order_book_utils import get_order_book_kraken
from poloniex.order_book_utils import get_order_book_poloniex

from bittrex.history_utils import get_history_bittrex
from kraken.history_utils import get_history_kraken
from poloniex.history_utils import get_history_poloniex


def get_ticker():

    timest = get_now_seconds()

    bittrex_tickers = {}
    for currency in BITTREX_CURRENCIES:
        ticker = get_ticker_bittrex(currency, timest)
        if ticker is not None:
            bittrex_tickers[ticker.pair_id] = ticker

    kraken_tickers = {}
    for currency in KRAKEN_CURRENCIES:
        ticker = get_ticker_kraken(currency, timest)
        if ticker is not None:
            kraken_tickers[ticker.pair_id] = ticker

    poloniex_tickers = {}
    for currency in POLONIEX_CURRENCIES:
        ticker = get_ticker_poloniex(currency, timest)
        if ticker is not None:
            poloniex_tickers[ticker.pair_id] = ticker

    return bittrex_tickers, kraken_tickers, poloniex_tickers


def get_ohlc():
    all_ohlc = []

    date_end = get_now_seconds()
    date_start = date_end

    for currency in BITTREX_CURRENCIES:
        period = "thirtyMin"
        all_ohlc += get_ohlc_bittrex(currency, date_end, date_start, period)

    for currency in KRAKEN_CURRENCIES:
        period = 15
        all_ohlc += get_ohlc_kraken(currency, date_end, date_start, period)

    for currency in POLONIEX_CURRENCIES:
        period = 14400
        all_ohlc += get_ohlc_poloniex(currency, date_end, date_start, period)

    return all_ohlc


def get_order_book(split_on_exchange=False):
    
    all_order_book = []
    
    poloniex_order_book = []
    kraken_order_book = []
    bittrex_order_book = []

    timest = get_now_seconds()

    for currency in POLONIEX_CURRENCIES:
        order_book = get_order_book_poloniex(currency, timest)
        if order_book is not None:
            if split_on_exchange == True:
		poloniex_order_book.append(order_book)	
	    else:
		all_order_book.append(order_book)

    for currency in KRAKEN_CURRENCIES:
        order_book = get_order_book_kraken(currency, timest)
        if order_book is not None:
            if split_on_exchange == True:
		kraken_order_book.append(order_book)	
	    else:
                all_order_book.append(order_book)

    for currency in BITTREX_CURRENCIES:
        order_book = get_order_book_bittrex(currency, timest)
        if order_book is not None:
            if split_on_exchange == True:
		bittrex_order_book.append(order_book)	
	    else:
            	all_order_book.append(order_book)

    if split_on_exchange == True:
	return poloniex_order_book, kraken_order_book, bittrex_order_book
    else:
    	return all_order_book

def get_history(prev_time, now_time):
    all_history = []

    for currency in POLONIEX_CURRENCIES:
        all_history += get_history_poloniex(currency, prev_time, now_time)

    for currency in KRAKEN_CURRENCIES:
        all_history += get_history_kraken(currency, prev_time, now_time)

    for currency in BITTREX_CURRENCIES:
        all_history += get_history_bittrex(currency, prev_time, now_time)

    return all_history
