class OrderBookUpdate:
    def __init__(self, sequence_id, bids, asks, trades_sell, trades_buy):
        self.sequence_id = sequence_id
        self.bids = bids
        self.asks = asks
        self.trades_sell = trades_sell
        self.trades_buy = trades_buy