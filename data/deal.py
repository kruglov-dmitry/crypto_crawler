from data.base_data import BaseData
from decimal import Decimal


class Deal(BaseData):
    def __init__(self, price, volume):
        self.price = Decimal(str(price))
        self.volume = Decimal(str(volume))

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.price == other.price
        return False

    def __str__(self):
        return "[price: {:16.8f} volume: {:16.8f} ]".format(self.price, self.volume)

    __repr__ = __str__
