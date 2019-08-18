import unittest

from enums.exchange import EXCHANGE
from enums.status import STATUS
from constants import API_KEY_PATH

from data.balance import Balance

from utils.key_utils import load_key_by_exchange, get_key_by_exchange
from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS

from huobi.balance_utils import get_balance_huobi
from huobi.market_utils import cancel_order_huobi
from huobi.buy_utils import add_buy_order_huobi
from huobi.sell_utils import add_sell_order_huobi
from huobi.order_utils import get_open_orders_huobi


class HuobiPrivateApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)
        load_key_by_exchange(API_KEY_PATH, EXCHANGE.HUOBI)
        self.huobi_key = get_key_by_exchange(EXCHANGE.HUOBI)

    def test_balance_retrieval(self):
        status, balance = get_balance_huobi(self.huobi_key)

        self.assertEquals(STATUS.SUCCESS, status)

        self.assertEquals(type(balance), Balance)

    def test_order_cancel(self):
        status, response = cancel_order_huobi(self.huobi_key, '00000000-0000-0000-0000-000000000000')

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("invalid-order-id" in str(response))

    def test_buy_order(self):
        status, response = add_buy_order_huobi(self.huobi_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("invalid-amount" in str(response) or "invalid-symbol" in str(response))

    def test_sell_order(self):
        status, response = add_sell_order_huobi(self.huobi_key, pair_name="NULL", price=0.0, amount=0.0)

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertTrue("invalid-amount" in str(response) or "invalid-symbol" in str(response))

    def test_open_orders_retrieval(self):
        status, orders = get_open_orders_huobi(self.huobi_key, pair_name='dashbtc')

        self.assertEquals(STATUS.SUCCESS, status)
        self.assertEquals(len(orders), 0)
