from data.base_data import BaseData
from constants import NO_MAX_CAP_LIMIT, NO_MIN_CAP_LIMIT


class MarketCap(BaseData):
    def __init__(self, pair_id, timest, min_volume_cap=NO_MIN_CAP_LIMIT, max_volume_cap=NO_MAX_CAP_LIMIT,
                 min_price_cap=NO_MIN_CAP_LIMIT, max_price_cap=NO_MAX_CAP_LIMIT):
        self.max_volume_cap = max_volume_cap
        self.min_volume_cap = min_volume_cap
        self.min_price_cap = min_price_cap
        self.max_price_cap = max_price_cap
        self.pair_id = pair_id
        self.last_updated = timest

    def get_max_volume_cap(self):
        return self.max_volume_cap

    def get_min_volume_cap(self):
        return self.min_volume_cap

    def update_time(self, timest):
        self.last_updated = timest

    def update_min_volume_cap(self, new_cap, cur_timest_sec):
        self.last_updated = cur_timest_sec
        self.min_volume_cap = new_cap

    def update_max_volume_cap(self, max_limit):
        self.max_volume_cap = max_limit
