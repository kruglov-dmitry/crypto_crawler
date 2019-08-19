import unittest

from enums.exchange import EXCHANGE
from enums.status import STATUS
from constants import API_KEY_PATH

from data.balance import Balance

from utils.key_utils import load_key_by_exchange, get_key_by_exchange
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from bittrex.balance_utils import get_balance_bittrex
from bittrex.market_utils import cancel_order_bittrex
from bittrex.buy_utils import add_buy_order_bittrex
from bittrex.sell_utils import add_sell_order_bittrex
from bittrex.order_utils import get_open_orders_bittrix
from bittrex.order_history import get_order_history_bittrex


class BittrexPrivateApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)
        load_key_by_exchange(API_KEY_PATH, EXCHANGE.BITTREX)
        self.bittrex_key = get_key_by_exchange(EXCHANGE.BITTREX)

    def test_balance_retrieval(self):
        status, balance = get_balance_bittrex(self.bittrex_key)

        self.assertEquals(STATUS.SUCCESS, status)

        self.assertEquals(type(balance), Balance)

    def test_order_cancel(self):
        status, response = cancel_order_bittrex(self.bittrex_key, '00000000-0000-0000-0000-000000000000')

        self.assertEquals(STATUS.SUCCESS, status)

        self.assertTrue("INVALID_ORDER" in str(response))

    def test_buy_order(self):
        status, response = add_buy_order_bittrex(self.bittrex_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("INVALID_MARKET" in str(response))

    def test_sell_order(self):
        status, response = add_sell_order_bittrex(self.bittrex_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("INVALID_MARKET" in str(response))

    def test_open_orders_retrieval(self):
        status, orders = get_open_orders_bittrix(self.bittrex_key, pair_name="NULL")
        self.assertEquals(STATUS.SUCCESS, status)
        self.assertEquals(len(orders), 0)

    def test_order_history_retrieval(self):
        status, orders = get_order_history_bittrex(self.bittrex_key, pair_name='NULL')
        self.assertEquals(STATUS.SUCCESS, status)
        self.assertEquals(len(orders), 0)
