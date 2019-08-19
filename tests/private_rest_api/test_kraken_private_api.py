import unittest

from enums.exchange import EXCHANGE
from enums.status import STATUS
from constants import API_KEY_PATH

from data.balance import Balance

from utils.key_utils import load_key_by_exchange, get_key_by_exchange
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from kraken.balance_utils import get_balance_kraken
from kraken.market_utils import cancel_order_kraken
from kraken.buy_utils import add_buy_order_kraken
from kraken.sell_utils import add_sell_order_kraken
from kraken.order_utils import get_open_orders_kraken
from kraken.order_history import get_order_history_kraken


class KrakenPrivateApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)
        load_key_by_exchange(API_KEY_PATH, EXCHANGE.KRAKEN)
        self.kraken_key = get_key_by_exchange(EXCHANGE.KRAKEN)

    def test_balance_retrieval(self):
        status, balance = get_balance_kraken(self.kraken_key)

        self.assertEquals(STATUS.SUCCESS, status)

        self.assertEquals(type(balance), Balance)

    def test_order_cancel(self):
        status, response = cancel_order_kraken(self.kraken_key, '00000000-0000-0000-0000-000000000000')

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("Invalid order'" in str(response))

    def test_buy_order(self):
        status, response = add_buy_order_kraken(self.kraken_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("Unknown asset pair" in str(response))

    def test_sell_order(self):
        status, response = add_sell_order_kraken(self.kraken_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("Unknown asset pair" in str(response))

    def test_open_orders_retrieval(self):
        status, orders = get_open_orders_kraken(self.kraken_key, pair_name="NULL")
        self.assertEquals(STATUS.SUCCESS, status)
        self.assertEquals(len(orders), 0)

    def test_order_history_retrieval(self):
        status, orders = get_order_history_kraken(self.kraken_key, pair_name='NULL')
        self.assertEquals(STATUS.SUCCESS, status)
        self.assertEquals(len(orders), 0)
