from BaseData import BaseData
from constants import FLOAT_POINT_PRECISION 


class Deal(BaseData):
    def __init__(self, price, volume):
        self.price = float(price)
        self.volume = float(volume)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            # FIXME ROUNDING
            return abs(self.price - other.price) < FLOAT_POINT_PRECISION
        return False
