KRAKEN_GET_TICKER = "https://api.kraken.com/0/public/Ticker?pair="

# OHLC ~ canddle stick urls
# https://api.kraken.com/0/public/OHLC?pair=XXRPXXBT&since=1497916800&interval=15
KRAKEN_GET_OHLC = "https://api.kraken.com/0/public/OHLC?pair="

# https://api.kraken.com/0/public/Depth?pair=XETHXXBT
KRAKEN_GET_ORDER_BOOK = "https://api.kraken.com/0/public/Depth?pair="

# https://api.kraken.com/0/public/Trades?pair=XETHXXBT&since=1501693512
KRAKEN_GET_HISTORY = "https://api.kraken.com/0/public/Trades?pair="

KRAKEN_CURRENCY_PAIRS = ["DASHXBT", "XETHXXBT", "XLTCXXBT", "XXRPXXBT", "BCHXBT", "XETCXXBT", "XZECXXBT", "XREPXXBT",
                         "XXMRXXBT", "XXDGXXBT",
                         "XETCXETH", "XREPXETH",
                         "DASHUSD", "XETHZUSD", "XLTCZUSD", "XXRPZUSD", "BCHUSD", "XETCZUSD", "XZECZUSD", "XXMRZUSD",
                         "USDTZUSD"
                         ]

KRAKEN_CURRENCIES = ["DASH", "BCH", "ZUSD", "XXBT", "EOS", "USDT", "XXRP", "XREP", "XETC", "XETH", "XXDG", "XZEC",
                     "XREP", "XXMR"]


KRAKEN_BASE_API_URL = "https://api.kraken.com"

KRAKEN_CANCEL_ORDER = "/0/private/CancelOrder"
KRAKEN_BUY_ORDER = "/0/private/AddOrder"
KRAKEN_SELL_ORDER = "/0/private/AddOrder"
KRAKEN_CHECK_BALANCE = "/0/private/Balance"

KRAKEN_GET_OPEN_ORDERS = "/0/private/OpenOrders"
KRAKEN_GET_CLOSE_ORDERS = "/0/private/ClosedOrders"
