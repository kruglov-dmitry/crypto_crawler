from BaseData import BaseData
from core.base_analysis import get_change
from enums.currency import CURRENCY
from utils.currency_utils import split_currency_pairs


class BalanceState(BaseData):
    def __init__(self, balance_per_exchange, balance_adjust_threshold):
        self.balance_per_exchange = balance_per_exchange
        self.balance_adjust_threshold = balance_adjust_threshold

    def is_there_disbalance(self, currency_id, src_exchange_id, dst_exchange_id, balance_threshold=None):

        # FIXME NOTE: I guess it should be excluded from overall fun
        if currency_id == CURRENCY.BITCOIN:
            return False

        # FIXME NOTE - add time checks here if it more than 2 minutes - should be at least some warning!
        difference = get_change(self.balance_per_exchange[src_exchange_id].balance[currency_id],
                                self.balance_per_exchange[dst_exchange_id].balance[currency_id],
                                provide_abs=False)

        if balance_threshold is None:
            balance_threshold = self.balance_adjust_threshold

        return difference > balance_threshold

    def add_balance(self, currency_id, exchange_id, volume):
        prev_volume = self.balance_per_exchange[exchange_id].balance[currency_id]
        self.balance_per_exchange[exchange_id].balance[currency_id] = volume + prev_volume

    def substract_balance(self, currency_id, exchange_id, volume):
        prev_volume = self.balance_per_exchange[exchange_id].balance[currency_id]
        self.balance_per_exchange[exchange_id].balance[currency_id] = prev_volume - volume

    def add_balance_by_pair(self, pair_id, exchange_id, volume, price):
        # i.e. we SELL src_currency_id for dst_currency_id
        src_currency_id, dst_currency_id = split_currency_pairs(pair_id)

        self.substract_balance(src_currency_id, exchange_id, volume * price)  # <<<==== bitcoin!

        self.add_balance(dst_currency_id, exchange_id, volume)

    def substract_balance_by_pair(self, pair_id, exchange_id, volume, price):
        # i.e. we SELL src_currency_id for dst_currency_id
        src_currency_id, dst_currency_id = split_currency_pairs(pair_id)
        self.substract_balance(dst_currency_id, exchange_id, volume)

        self.add_balance(src_currency_id, exchange_id, volume * price) # <<<==== bitcoin!

    def do_we_have_enough_by_pair(self, pair_id, exchange_id, volume, price):

        # i.e. we are going to BUY volume of dst_currency by price
        # using src_currency so we have to adjust volume

        src_currency_id, dst_currency_id = split_currency_pairs(pair_id)

        self.do_we_have_enough(src_currency_id, exchange_id, volume * price)

    def do_we_have_enough(self, currency_id, exchange_id, volume):
        return self.balance_per_exchange[exchange_id].balance[currency_id] <= volume

    def get_volume_by_pair_id(self, pair_id, exchange_id):
        src_currency_id, dst_currency_id = split_currency_pairs(pair_id)
        return self.balance_per_exchange[exchange_id].balance[src_currency_id]
