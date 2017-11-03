from BaseData import BaseData
from utils.currency_utils import get_currency_name_by_id
from utils.currency_utils import split_currency_pairs


class MarketCap(BaseData):
    def __init__(self, min_volume_cap, max_volume_cap, min_price_cap, max_price_cap):
        self.max_volume_cap = max_volume_cap.copy()
        self.min_volume_cap = min_volume_cap.copy()
        self.min_price_cap = min_price_cap.copy()
        self.max_price_cap = max_price_cap.copy()

    def __str__(self):
        str_repr = "MarketCap common for all exchanges. Minimum capacity: \n"

        for currency_id in self.min_volume_cap:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.min_volume_cap[currency_id])

        str_repr += " Max capacity:\n"
        for currency_id in self.max_volume_cap:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.max_volume_cap[currency_id])

        return str_repr

    def is_deal_size_acceptable(self, pair_id, dst_currency_volume, sell_price, buy_price):
        """
        We are going to operate with VOLUME
        at first exchange we will sell DST_CURRENCY for SRC_CURRENCY using SELL_PRICE
        at second exchange we will buy DST_CURRENCY for SRC_CURRENCY using BUY_PRICE
        :param pair_id:
        :param dst_currency_volume:
        :param sell_price:
        :param buy_price:
        :return:
        """

        # FIXME NOTE: sell_price not handled in any way now

        bitcoin_id, dst_currency_id = split_currency_pairs(pair_id)

        # total_deal_cost_within_cap = self.is_total_deal_cost_within_cap(bitcoin_id, dst_currency_volume, buy_price) and \
        #                             self.is_total_deal_cost_within_cap(dst_currency_id, dst_currency_volume, sell_price)

        volume_within_cap = self.is_deal_volume_within_cap(dst_currency_id, dst_currency_volume) and \
                            self.is_deal_volume_within_cap(bitcoin_id, dst_currency_volume * buy_price)

        #return total_deal_cost_within_cap and volume_within_cap
        return volume_within_cap

    def is_total_deal_cost_within_cap(self, bitcoin_id, volume, price):
        deal_value = volume * price
        return self.min_price_cap[bitcoin_id] < deal_value < self.max_price_cap[bitcoin_id]

    def is_deal_volume_within_cap(self, currency_id, volume):
        return self.min_volume_cap[currency_id] < volume < self.max_volume_cap[currency_id]

    def get_max_volume_cap_by_dst(self, pair_id):
        bitcoin_id, dst_currency_id = split_currency_pairs(pair_id)
        return self.max_volume_cap[dst_currency_id]



