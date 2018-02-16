import multiprocessing
from enums.currency import CURRENCY
from enums.currency_pair import CURRENCY_PAIR

SECONDS_IN_WEEK = 604800
SECONDS_IN_DAY = 86400

HTTP_TIMEOUT_SECONDS = 25
DEAL_MAX_TIMEOUT = 10

ZERO_BALANCE = 0.0
ARBITRAGE_CURRENCY = CURRENCY.values()
ARBITRAGE_PAIRS = CURRENCY_PAIR.values()

CACHE_HOST = "54.193.19.230"
#CACHE_HOST = "192.168.1.106"
CACHE_PORT = 6379

CORE_NUM = multiprocessing.cpu_count()
POOL_SIZE = 8 * CORE_NUM

LOGS_FOLDER = "./logs/"


# FIXME NOTE: arbitrage_core
# This is indexes for comparison bid\ask within order books
# yeap, global constants is very bad
FIRST = 0
LAST = 0

BALANCE_EXPIRED_THRESHOLD = 60
MIN_CAP_UPDATE_TIMEOUT = 900
NO_MAX_CAP_LIMIT = 0

START_OF_TIME = -1


FLOAT_POINT_PRECISION = 0.00000001

HEARTBEAT_TIMEOUT = 60
