class DEAL_TYPE:
    SELL = 1
    BUY = 2


def get_deal_type_by_id(deal_id):
    return {
        DEAL_TYPE.BUY: "Buy",
        DEAL_TYPE.SELL: "Sell"
    }[deal_id]
