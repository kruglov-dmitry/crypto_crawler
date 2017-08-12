from BaseData import BaseData

class Deal(BaseData):
    def __init__(self, price, volume):
        self.price = float(price)
        self.volume = float(volume)