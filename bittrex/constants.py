
BITTREX_GET_TICKER = "https://bittrex.com/api/v1.1/public/getticker?market="

# OHLC ~ canddle stick urls
# https://bittrex.com/Api/v2.0/pub/market/GetTicks?tickInterval=oneMin&marketName=BTC-ETH&_=timest
BITTREX_GET_OHLC = "https://bittrex.com/Api/v2.0/pub/market/GetTicks?tickInterval="

#       FIXME NOTE - depth can vary
# https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both
BITTREX_GET_ORDER_BOOK = "https://bittrex.com/api/v1.1/public/getorderbook?type=both&market="

# https://bittrex.com/api/v1.1/public/getmarkethistory?market=BTC-LTC
BITTREX_GET_HISTORY = "https://bittrex.com/api/v1.1/public/getmarkethistory?market="

BITTREX_CURRENCIES = ["BTC-DASH", "BTC-ETH", "BTC-LTC", "BTC-XRP", "BTC-BCC", "BTC-ETC", "BTC-SC", "BTC-DGB",
                      "BTC-XEM", "BTC-ARDR"]

# https://bittrex.com/api/v1.1/market/buylimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3
BITTREX_BUY_ORDER = "https://bittrex.com/api/v1.1/market/buylimit?apikey="

# https://bittrex.com/api/v1.1/market/selllimit?apikey=API_KEY&market=BTC-LTC&quantity=1.2&rate=1.3    
BITTREX_SELL_ORDER = "https://bittrex.com/api/v1.1/market/selllimit?apikey="

# https://bittrex.com/api/v1.1/market/cancel?apikey=API_KEY&uuid=ORDER_UUID
BITTREX_CANCEL_ORDER = "https://bittrex.com/api/v1.1/market/cancel?apikey="
