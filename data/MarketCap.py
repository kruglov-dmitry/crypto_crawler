from BaseData import BaseData
from utils.currency_utils import get_currency_name_by_id
from utils.currency_utils import split_currency_pairs


class MarketCap(BaseData):
    def __init__(self, min_volume_cap, max_volume_cap, min_price_cap, max_price_cap, timest):
        self.max_volume_cap = max_volume_cap.copy()
        self.min_volume_cap = min_volume_cap.copy()
        self.min_price_cap = min_price_cap.copy()
        self.max_price_cap = max_price_cap.copy()
        self.last_updated = timest

    def __str__(self):
        str_repr = "MarketCap common for all exchanges. Minimum capacity: \n"

        for currency_id in self.min_volume_cap:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.min_volume_cap[currency_id])

        str_repr += " Max capacity:\n"
        for currency_id in self.max_volume_cap:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.max_volume_cap[currency_id])

        return str_repr

    def get_max_volume_cap_by_dst(self, pair_id):
        base_currency_id, dst_currency_id = split_currency_pairs(pair_id)
        return self.max_volume_cap[dst_currency_id]

    def get_min_volume_cap_by_dst(self, pair_id):
        base_currency_id, dst_currency_id = split_currency_pairs(pair_id)
        return self.min_volume_cap[dst_currency_id]

    def get_max_volume_by_currency_id(self, currency_id):
        return self.max_volume_cap[currency_id]

    def get_min_volume_by_currency_id(self, currency_id):
        return self.min_volume_cap[currency_id]

    def update_time(self, timest):
        self.last_updated = timest

    def update_min_cap(self, currency_id, new_cap, cur_timest_sec):
        self.last_updated = cur_timest_sec
        self.min_volume_cap[currency_id] = new_cap

    def get_min_cap(self, currency_id):
        if currency_id in self.min_volume_cap:
            return self.min_volume_cap[currency_id]
        return None
