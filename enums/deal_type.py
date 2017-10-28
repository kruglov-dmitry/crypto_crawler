class DEAL_TYPE:
    SELL = 1
    BUY = 2
    ARBITRAGE = 3
    REVERSE = 4


def get_deal_type_by_id(deal_id):
    return {
        DEAL_TYPE.BUY: "Buy",
        DEAL_TYPE.SELL: "Sell",
        DEAL_TYPE.ARBITRAGE: "Arbitrage",
        DEAL_TYPE.REVERSE: "Reverse"
    }[deal_id]
