from data.BaseData import BaseData
from utils.exchange_utils import get_exchange_id_by_name


class ExchangeArbitrageSettings(BaseData):
    def __init__(self, src_exchange_name, dst_exchange_name, list_of_pairs):
        self.src_exchange_name = src_exchange_name
        self.src_exchange_id = get_exchange_id_by_name(self.src_exchange_name)
        self.dst_exchange_name = dst_exchange_name
        self.dst_exchange_id = get_exchange_id_by_name(self.dst_exchange_name)
        self.list_of_pairs = list_of_pairs