from BaseData import BaseData
import copy


class OrderState(BaseData):
    def __init__(self, exchange_id, timest, open_orders, closed_orders):
        self.exchange_id = exchange_id
        self.timest = timest
        self.open_orders = copy.deepcopy(open_orders)
        self.closed_orders = copy.deepcopy(closed_orders)

    def get_num_of_open_orders(self):
        cnt = 0
        for k in self.open_orders:
            cnt += len(self.open_orders[k])

        return cnt

    def get_num_of_closed_orders(self):
        cnt = 0
        for k in self.closed_orders:
            cnt += len(self.closed_orders[k])

        return cnt

    def get_total_num_of_orders(self):
        return self.get_num_of_closed_orders() + self.get_num_of_open_orders()