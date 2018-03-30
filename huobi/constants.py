HUOBI_API_ONLY = "api.huobi.pro"
HUOBI_API_URL = "https://" + HUOBI_API_ONLY

HUOBI_GET_TICKER = HUOBI_API_URL + "/market/detail/merged?symbol="

# 1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year
# market/history/kline?period=1day&size=200&symbol=btcusdt
HUOBI_GET_OHLC = HUOBI_API_URL + "/market/history/kline?symbol="

HUOBI_GET_ORDER_BOOK = HUOBI_API_URL + "/market/depth?symbol="

HUOBI_GET_HISTORY = HUOBI_API_URL + "/market/history/trade?symbol="

HUOBI_CURRENCY_PAIRS = ['dashbtc', 'ethbtc', 'ltcbtc', 'xrpbtc', 'bchbtc', 'etcbtc', 'xembtc', 'omgbtc', 'zecbtc',
                        'neobtc', 'qtumbtc', 'btgbtc', 'batbtc', 'rcnbtc', 'zrxbtc', 'lskbtc', 'engbtc', 'trxbtc',
                        'omgeth', 'qtumeth', 'bateth', 'rcneth', 'engeth', 'trxeth',
                        'dashusdt', 'btcusd', 'ltcusdt', 'xrpusdt', 'bchusdt', 'etcusdt', 'omgusdt', 'qtumusdt',
                        'ethusdt', 'zecusdt', 'neousdt'
                        ]

HUOBI_BUY_ORDER = "/v1/order/orders/place"

HUOBI_SELL_ORDER = "/v1/order/orders/place"

HUOBI_CANCEL_ORDER = "/v1/order/orders/"

HUOBI_CHECK_BALANCE = "/v1/account/accounts/{account-id}/balance"

HUOBI_GET_OPEN_ORDERS = "/v1/order/orders"

HUOBI_GET_TRADE_HISTORY = "/v1/order/orders"

HUOBI_NUM_OF_DEAL_RETRY = 1
HUOBI_DEAL_TIMEOUT = 5

HUOBI_GET_ACCOUNT_INFO = "/v1/account/accounts?"

HUOBI_ACOUNT_ID = "huobi_account_id"

EMPTY_LIST = []

HUOBI_ORDER_HISTORY_LIMIT = 100
