from Deal import Deal
from enums.deal_type import get_deal_type_by_id
from utils.currency_utils import get_currency_name_by_id
from utils.exchange_utils import get_exchange_name_by_id


class Trade(Deal):
    def __init__(self, trade_type, exchange_id, pair_id, price, volume):
        self.trade_type = trade_type
        self.exchange_id = exchange_id
        self.pair_id = pair_id
        self.price = price
        self.volume = volume

    def __str__(self):
        str_repr = "Trade at Exchange: {exch} type: {deal_type} pair: {pair} for volume {vol} with price {price}".format(
            exch=get_exchange_name_by_id(self.exchange_id),
            deal_type=get_deal_type_by_id(self.trade_type),
            pair=get_currency_name_by_id(self.pair_id),
            vol=self.volume,
            price=self.price)

        return str_repr

    def set_deal_id(self, deal_id):
        self.deal_id = deal_id

    @classmethod
    def load_from_market(cls):
        pass
