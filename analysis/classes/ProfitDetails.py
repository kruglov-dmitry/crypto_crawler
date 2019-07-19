from utils.currency_utils import get_currency_name_by_id
from utils.string_utils import float_to_str


class ProfitDetails:
    def __init__(self, base_currency_id, dst_currency_id, pair_id, profit_in_coin, profit_in_base_currency):
        self.base_currency_id = base_currency_id
        self.dst_currency_id = dst_currency_id
        self.pair_id = pair_id
        self.profit_in_coin = profit_in_coin
        self.profit_in_base_currency = profit_in_base_currency

    def __str__(self):
        return """Profit in {coin_name}: {profit_coin} Profit in {base_name}: {profit_base} """.format(
            coin_name=get_currency_name_by_id(self.dst_currency_id),
            profit_coin=float_to_str(self.profit_in_coin),
            base_name=get_currency_name_by_id(self.base_currency_id),
            profit_base=float_to_str(self.profit_in_base_currency))
