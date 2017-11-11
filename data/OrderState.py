from BaseData import BaseData
import copy


class OrderState(BaseData):
    def __init__(self, exchange_id, timest, open_orders, closed_orders):
        self.exchange_id = exchange_id
        self.timest = timest
        self.open_orders = copy.deepcopy(open_orders)
        self.closed_orders = copy.deepcopy(closed_orders)

    def get_num_of_open_orders(self):
        return len(self.open_orders)

    def get_num_of_closed_orders(self):
        return len(self.closed_orders)

    def get_total_num_of_orders(self):
        return self.get_num_of_closed_orders() + self.get_num_of_open_orders()