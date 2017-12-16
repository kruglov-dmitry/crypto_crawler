from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id
from enums.deal_type import get_deal_type_by_id


class ArbitrageConfig:
    def __init__(self, threshold, sell_exchange_id, buy_exchange_id, pair_id, mode_id):
        self.threshold = threshold
        self.sell_exchange_id = sell_exchange_id
        self.buy_exchange_id = buy_exchange_id
        self.pair_id = pair_id
        self.mode = mode_id

    def __str__(self):
        str_repr = "Sell=Bid exchange - {sell_exch} id = {id1} Buy-Ask exchange - {buy_exch} " \
                   "id = {id2} currency pair - {pair} Arbitrage Threshold = {thrshld} mode = {md} id = {id3}".format(
            sell_exch=get_exchange_name_by_id(self.sell_exchange_id),
            id1=self.sell_exchange_id,
            buy_exch=get_exchange_name_by_id(self.buy_exchange_id),
            id2=self.buy_exchange_id,
            pair=get_pair_name_by_id(self.pair_id),
            pair_id = self.pair_id,
            thrshld=self.threshold,
            md=get_deal_type_by_id(self.mode),
            id3=self.mode
        )

        return str_repr