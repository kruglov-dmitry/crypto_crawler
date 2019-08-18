import unittest

from enums.exchange import EXCHANGE
from enums.status import STATUS
from constants import API_KEY_PATH

from data.balance import Balance

from utils.key_utils import load_key_by_exchange, get_key_by_exchange
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from poloniex.balance_utils import get_balance_poloniex
from poloniex.market_utils import cancel_order_poloniex
from poloniex.buy_utils import add_buy_order_poloniex
from poloniex.sell_utils import add_sell_order_poloniex
from poloniex.order_utils import get_open_orders_poloniex


class PoloniexPrivateApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)
        load_key_by_exchange(API_KEY_PATH, EXCHANGE.POLONIEX)
        self.poloniex_key = get_key_by_exchange(EXCHANGE.POLONIEX)

    def test_balance_retrieval(self):
        status, balance = get_balance_poloniex(self.poloniex_key)

        self.assertEquals(STATUS.SUCCESS, status)

        self.assertEquals(type(balance), Balance)

    def test_order_cancel(self):
        status, response = cancel_order_poloniex(self.poloniex_key, '00000000-0000-0000-0000-000000000000')

        # 422 Unprocessable Entity response status code
        # indicates that the server understands the content type of the request entity,
        # and the syntax of the request entity is correct,
        # but it was unable to process the contained instructions.
        self.assertEquals(STATUS.FAILURE, status)
        self.assertTrue("Invalid orderNumber parameter" in str(response))

    def test_buy_order(self):
        status, response = add_buy_order_poloniex(self.poloniex_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.FAILURE, status)
        self.assertTrue("Invalid currencyPair parameter" in str(response))

    def test_sell_order(self):
        status, response = add_sell_order_poloniex(self.poloniex_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.FAILURE, status)
        self.assertTrue("Invalid currencyPair parameter" in str(response))

    def test_open_orders_retrieval(self):
        status, orders = get_open_orders_poloniex(self.poloniex_key, pair_name="NULL")

        self.assertEquals(STATUS.FAILURE, status)
        self.assertEquals(len(orders), 0)
