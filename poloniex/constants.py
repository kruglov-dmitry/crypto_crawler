# ticker urls
POLONIEX_GET_TICKER = "https://poloniex.com/public?command=returnTicker"  #  Yeah, it just return EVERYTHING

# OHLC ~ canddle stick urls
#  https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
POLONIEX_GET_OHLC = "https://poloniex.com/public?command=returnChartData&currencyPair="

#       FIXME NOTE - depth can vary
# https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10, depth optional
POLONIEX_GET_ORDER_BOOK = "https://poloniex.com/public?command=returnOrderBook&currencyPair="

# https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1501693512&end=1501693572
POLONIEX_GET_HISTORY = "https://poloniex.com/public?command=returnTradeHistory&currencyPair="

POLONIEX_CURRENCIES = ["BTC_DASH", "BTC_ETH", "BTC_LTC", "BTC_XRP", "BTC_ETC", "BTC_SC", "BTC_DGB", "BTC_XEM",
                       "BTC_ARDR", "BTC_BCH", "BTC_OMG", "BTC_ZEC", "BTC_REP",
                       "ETH_ETC", "ETH_BCH", "ETH_OMG", "ETH_ZEC", "ETH_REP",
                       "USDT_DASH", "USDT_ETH", "USDT_LTC", "USDT_XRP", "USDT_ETC", "USDT_BCH", "USDT_ZEC", "USDT_REP"
                       ]

POLONIEX_TRADING_API = "https://poloniex.com/tradingApi"

POLONIEX_CANCEL_ORDER = POLONIEX_TRADING_API
POLONIEX_BUY_ORDER = POLONIEX_TRADING_API
POLONIEX_SELL_ORDER = POLONIEX_TRADING_API
POLONIEX_CHECK_BALANCE = POLONIEX_TRADING_API
