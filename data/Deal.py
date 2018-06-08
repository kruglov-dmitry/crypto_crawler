from BaseData import BaseData


class Deal(BaseData):
    def __init__(self, price, volume):
        self.price = float(price)
        self.volume = float(volume)

    def __lt__(self, other):
        """
        Used by biset.insert to maintain ordered asks\bids of order book
        :param other:
        :return:
        """
        return self.price < other.price
