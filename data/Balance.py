from BaseData import BaseData
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_name_by_id

"""

time_of_last_update,

exchange_id -> {
    pair_id: volume,
    pair_id: volume,
    ... ,
    pair_id: volume
}, 

    .....

exchange_id -> {
    pair_id: volume,
    pair_id: volume,
    ... ,
    pair_id: volume
},

"""


class Balance(BaseData):
    def __init__(self, last_update):
        self.last_update = last_update

    @classmethod
    def from_poloniex(cls, last_update, json_document):
        return Balance(last_update)

    @classmethod
    def from_kraken(cls, last_update, json_document):
        return Balance(last_update)

    @classmethod
    def from_bitriex(cls, last_update, json_document):
        return Balance(last_update)

    def update_from_poloniex(self, last_update, json_document):
        self.last_update = last_update
        pass

    def update_kraken(self, last_update, json_document):
        self.last_update = last_update
        pass

    def update_bitriex(self, last_update, json_document):
        self.last_update = last_update
        pass

    def is_there_disbalance(self, pair_id, threshold):
        # FIXME check accros all exchange
        return True