from Deal import Deal
from enums.deal_type import get_deal_type_by_id
from utils.currency_utils import get_currency_name_by_id
from utils.exchange_utils import get_exchange_name_by_id


class Trade(Deal):
    def __init__(self, trade_type, exchange_id, pair_id, price, volume, order_book_time, create_time, execute_time=None):
        self.trade_type = trade_type
        self.exchange_id = exchange_id
        self.pair_id = pair_id
        self.price = price
        self.volume = volume
        self.order_book_time = order_book_time
        self.create_time = create_time
        self.execute_time = execute_time

    def __str__(self):
        str_repr = "Trade at Exchange: {exch} type: {deal_type} pair: {pair} for volume {vol} with price {price} " \
                   "order_book_time {ob_time} create_time {ct_time} execute_time {ex_time}".format(
            exch=get_exchange_name_by_id(self.exchange_id),
            deal_type=get_deal_type_by_id(self.trade_type),
            pair=get_currency_name_by_id(self.pair_id),
            vol=self.volume,
            price=self.price,
            ob_time=self.order_book_time,
            ct_time=self.create_time,
            ex_time=self.execute_time)

        return str_repr

    def set_deal_id(self, deal_id):
        self.deal_id = deal_id

    @classmethod
    def load_from_market(cls):
        pass
