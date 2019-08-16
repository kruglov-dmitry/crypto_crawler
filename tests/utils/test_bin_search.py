import unittest

from analysis.binary_search import binary_search
from data.deal import Deal
from data.order_book import cmp_method_ask, cmp_method_bid

from utils.debug_utils import set_logging_level, LOG_ALL_ERRORS


class BinarySearchTests(unittest.TestCase):
    def setUp(self):
        set_logging_level(LOG_ALL_ERRORS)

        self.first = Deal(0.03172795, 0.1)
        self.non_present = Deal(10.1, 0.1)
        self.deal_update = Deal(0.03172801, 0.4)

        unsorted = [self.first, Deal(0.03172796, 0.2), Deal(0.03172798, 0.3),
                    self.deal_update, Deal(0.03173, 0.5)]

        self.asks = sorted(unsorted, key=lambda x: x.price, reverse=False)
        self.bids = sorted(unsorted, key=lambda x: x.price, reverse=True)

    def test_bin_search_asks(self):
        item_insert_point = binary_search(self.asks, self.first, cmp_method_ask)

        self.assertEquals(item_insert_point, 0)

    def test_bin_search_asks_not_present(self):
        item_insert_point = binary_search(self.asks, self.non_present, cmp_method_ask)

        self.assertEquals(item_insert_point, len(self.asks))

    def test_bin_search_asks_update_present(self):
        idx = binary_search(self.asks, self.deal_update, cmp_method_ask)

        is_present = False
        if idx < len(self.asks):
            is_present = self.asks[idx] == self.deal_update

        self.assertTrue(is_present)

    def test_bin_search_bids(self):
        item_insert_point = binary_search(self.bids, self.first, cmp_method_bid)

        self.assertEquals(item_insert_point, -1 + len(self.bids))

    def test_bin_search_bids_not_present(self):

        item_insert_point = binary_search(self.bids, self.non_present, cmp_method_bid)

        self.assertEquals(item_insert_point, 0)

    def test_bin_search_bids_update_present(self):
        idx = binary_search(self.bids, self.deal_update, cmp_method_bid)

        is_present = False
        if idx < len(self.bids):
            is_present = self.bids[idx] == self.deal_update

        self.assertTrue(is_present)
