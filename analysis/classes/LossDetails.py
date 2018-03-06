from utils.currency_utils import get_pair_name_by_id, get_currency_name_by_id
from utils.string_utils import float_to_str


class LossDetails():
    def __init__(self, base_currency_id, dst_currency_id, pair_id, loss_in_coin, loss_in_base_currency):
        self.base_currency_id = base_currency_id
        self.dst_currency_id = dst_currency_id
        self.pair_id = pair_id
        self.loss_in_coin = loss_in_coin
        self.loss_in_base_currency = loss_in_base_currency

    def __str__(self):
        return """Loss in {coin_name}: {profit_coin} Loss in {base_name}: {profit_base} """.format(
            coin_name=get_currency_name_by_id(self.dst_currency_id),
            profit_coin=float_to_str(self.loss_in_coin),
            base_name=get_currency_name_by_id(self.base_currency_id),
            profit_base=float_to_str(self.loss_in_base_currency))