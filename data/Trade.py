from Deal import Deal


class Trade(Deal):
    def __init__(self, trade_type, exchange_id, pair_id, price, volume):
        self.trade_type = trade_type
        self.exchange_id = exchange_id
        self.pair_id = pair_id
        self.price = price
        self.volume = volume

    def set_deal_id(self, deal_id):
        self.deal_id = deal_id

    @classmethod
    def load_from_market(cls):
        pass