import unittest

from enums.exchange import EXCHANGE
from enums.status import STATUS
from constants import API_KEY_PATH

from data.balance import Balance

from utils.key_utils import load_key_by_exchange, get_key_by_exchange
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from binance.balance_utils import get_balance_binance
from binance.market_utils import cancel_order_binance
from binance.buy_utils import add_buy_order_binance
from binance.sell_utils import add_sell_order_binance
from binance.order_utils import get_open_orders_binance


class BinancePrivateApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)
        load_key_by_exchange(API_KEY_PATH, EXCHANGE.BINANCE)
        self.binance_key = get_key_by_exchange(EXCHANGE.BINANCE)

    def test_balance_retrieval(self):
        status, balance = get_balance_binance(self.binance_key)

        self.assertEquals(STATUS.SUCCESS, status)

        self.assertEquals(type(balance), Balance)

    def test_order_cancel(self):
        status, response = cancel_order_binance(self.binance_key, pair_name="NULL", order_id='1234567890')

        self.assertEquals(STATUS.FAILURE, status)
        self.assertTrue("Invalid symbol" in str(response))

    def test_buy_order(self):
        status, response = add_buy_order_binance(self.binance_key, pair_name="NULL", price=0.0, amount=0.0)

        # 400 Bad Request response status code indicates
        # that the server cannot or will not process the request

        self.assertEquals(STATUS.FAILURE, status)
        self.assertTrue("Invalid symbol" in str(response))

    def test_sell_order(self):
        status, response = add_sell_order_binance(self.binance_key, pair_name="NULL", price=0.0, amount=0.0)
        self.assertEquals(STATUS.FAILURE, status)
        self.assertTrue("Invalid symbol" in str(response))

    def test_open_orders_retrieval(self):
        status, orders = get_open_orders_binance(self.binance_key, pair_name='NULL')
        self.assertEquals(STATUS.FAILURE, status)
        self.assertEquals(len(orders), 0)
