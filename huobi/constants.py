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
                        'eosbtc', 'icxbtc', 'rdnbtc', 'qspbtc', 'ontbtc', 'hsrbtc', 'zilbtc', 'venbtc', 'elfbtc',
                        'blzbtc', 'reqbtc', 'linkbtc', 'nasbtc', 'elabtc', 'adabtc',
                        'omgeth', 'qtumeth', 'bateth', 'rcneth', 'engeth', 'trxeth', 'eoseth', 'icxeth', 'rdneth',
                        'qspeth', 'onteth', 'hsreth', 'zileth', 'veneth', 'elfeth', 'blzeth', 'reqeth', 'linketh',
                        'lsketh', 'naseth', 'elaeth', 'adaeth',
                        'dashusdt', 'btcusdt', 'ltcusdt', 'xrpusdt', 'bchusdt', 'etcusdt', 'omgusdt', 'qtumusdt',
                        'ethusdt', 'zecusdt', 'neousdt', 'eosusdt', 'hsrusdt', 'zilusdt', 'venusdt', 'elfusdt',
                        'nasusdt', 'elausdt', 'adausdt']

HUOBI_BUY_ORDER = "/v1/order/orders/place"

HUOBI_SELL_ORDER = "/v1/order/orders/place"

HUOBI_CANCEL_ORDER = "/v1/order/orders/"

HUOBI_CHECK_BALANCE = "/v1/account/accounts/"

HUOBI_GET_OPEN_ORDERS = "/v1/order/orders"

# /v1/order/orders/{order-id}/matchresults
HUOBI_GET_ORDER_DETAILS = "/v1/order/orders/"

HUOBI_GET_TRADE_HISTORY = "/v1/order/orders"

HUOBI_NUM_OF_DEAL_RETRY = 1
HUOBI_DEAL_TIMEOUT = 5

HUOBI_GET_ACCOUNT_INFO = "/v1/account/accounts"

HUOBI_ACOUNT_ID = "huobi_account_id"

EMPTY_LIST = []

HUOBI_ORDER_HISTORY_LIMIT = 100

HUOBI_POST_HEADERS = {'content-type': 'application/json', 'accept': 'application/json'}
HUOBI_GET_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

HUOBI_WEBSOCKET_URL = "wss://api.huobipro.com/ws"
HUOBI_SUBSCRIPTION_STRING = """{{"sub": "market.{pair_name}.depth.step0","id": "{uuid_id}"}}"""
