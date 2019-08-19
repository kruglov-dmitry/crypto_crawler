import threading
import unittest

from enums.currency_pair import CURRENCY_PAIR
from bittrex.socket_api import SubscriptionBittrex

from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS
from utils.time_utils import sleep_for


class BittrexSocketApiTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)

    def test_socket_subscription(self):
        t1 = SubscriptionBittrex(CURRENCY_PAIR.BTC_TO_ETC)
        buy_subscription_thread = threading.Thread(target=t1.subscribe, args=())
        buy_subscription_thread.daemon = True
        buy_subscription_thread.start()

        sleep_for(5)
        self.assertTrue(t1.should_run)

        t1.disconnect()
        self.assertFalse(t1.should_run)
