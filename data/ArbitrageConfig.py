from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id
from enums.deal_type import get_deal_type_by_id


class ArbitrageConfig:
    def __init__(self, threshold, reverse_threshold, sell_exchange_id, buy_exchange_id, pair_id):
        self.threshold = threshold
        self.reverse_threshold = reverse_threshold
        self.sell_exchange_id = sell_exchange_id
        self.buy_exchange_id = buy_exchange_id
        self.pair_id = pair_id
        self.log_file_name = self._generate_file_name()

    def __str__(self):
        str_repr = """Sell=Bid exchange - {sell_exch} id = {id1} Buy-Ask exchange - {buy_exch}
        id = {id2} currency pair - {pair} Arbitrage Threshold = {thrshld} Reverse Threshold = {rv_thr}
        log_file_name = {log_file_name}""".format(
            sell_exch=get_exchange_name_by_id(self.sell_exchange_id),
            id1=self.sell_exchange_id,
            buy_exch=get_exchange_name_by_id(self.buy_exchange_id),
            id2=self.buy_exchange_id,
            pair=get_pair_name_by_id(self.pair_id),
            pair_id = self.pair_id,
            thrshld=self.threshold,
            rv_thr=self.reverse_threshold,
            log_file_name=self.log_file_name
        )

        return str_repr

    def _generate_file_name(self):
        return "{sell_exch}==>{buy_exch}-{pair_name}.log".format(
            sell_exch=get_exchange_name_by_id(self.sell_exchange_id),
            buy_exch=get_exchange_name_by_id(self.buy_exchange_id),
            pair_name=get_pair_name_by_id(self.pair_id)
        )