from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id
from debug_utils import get_debug_level_name_by_id
from constants import BALANCE_UPDATE_TIMEOUT, MIN_CAP_UPDATE_TIMEOUT


class ArbitrageConfig:
    def __init__(self, sell_exchange_id, buy_exchange_id, pair_id, threshold, reverse_threshold, balance_threshold,
                 deal_expire_timeout, cfg_file_name, cap_update_timeout=MIN_CAP_UPDATE_TIMEOUT,
                 balance_update_timeout=BALANCE_UPDATE_TIMEOUT):
        self.threshold = threshold
        self.reverse_threshold = reverse_threshold
        self.balance_threshold = balance_threshold
        self.sell_exchange_id = sell_exchange_id
        self.buy_exchange_id = buy_exchange_id
        self.pair_id = pair_id
        self.deal_expire_timeout = deal_expire_timeout
        self.cfg_file_name = cfg_file_name
        self.log_file_name = self._generate_file_name()

        self.cap_update_timeout = cap_update_timeout
        self.balance_update_timeout = balance_update_timeout

    def __str__(self):
        str_repr = """Sell=Bid exchange - {sell_exch} id = {id1} Buy-Ask exchange - {buy_exch} id = {id2} 
        currency pair - {pair} Arbitrage Threshold = {thrshld} Reverse Threshold = {rv_thr} Balance Threshold = {b_thr}
        deal_expire_timeout = {deal_expire_timeout}
        cfg_file_name = {cfg_file_name}
        log_file_name = {log_file_name}
        cap_update_timeout = {cap_update_timeout}
        balance_update_timeout = {balance_update_timeout}
        """.format(
            sell_exch=get_exchange_name_by_id(self.sell_exchange_id),
            id1=self.sell_exchange_id,
            buy_exch=get_exchange_name_by_id(self.buy_exchange_id),
            id2=self.buy_exchange_id,
            pair=get_pair_name_by_id(self.pair_id),
            pair_id = self.pair_id,
            thrshld=self.threshold,
            rv_thr=self.reverse_threshold,
            b_thr=self.balance_threshold,
            cfg_file_name=get_debug_level_name_by_id(self.cfg_file_name),
            deal_expire_timeout=self.deal_expire_timeout,
            log_file_name=self.log_file_name,
            cap_update_timeout=self.cap_update_timeout,
            balance_update_timeout=self.balance_update_timeout
        )

        return str_repr

    def _generate_file_name(self):
        return "{sell_exch}==>{buy_exch}-{pair_name}.log".format(
            sell_exch=get_exchange_name_by_id(self.sell_exchange_id),
            buy_exch=get_exchange_name_by_id(self.buy_exchange_id),
            pair_name=get_pair_name_by_id(self.pair_id)
        )

    def generate_window_name(self):
        window_name = "{pair_id} - {pair_name}".format(pair_id=self.pair_id,
                                                       pair_name=get_pair_name_by_id(self.pair_id))
        return window_name

    def generate_command(self, full_path_to_script):
        cmd = "{cmd} --threshold {threshold} --reverse_threshold {reverse_threshold} --balance_threshold " \
              "{balance_threshold} --sell_exchange_id {sell_exchange_id} --buy_exchange_id {buy_exchange_id} " \
              "--pair_id {pair_id} --deal_expire_timeout {deal_expire_timeout} " \
              "--cfg {cfg}".format(cmd=full_path_to_script,
                                   threshold=self.threshold,
                                   reverse_threshold=self.reverse_threshold,
                                   balance_threshold=self.balance_threshold,
                                   sell_exchange_id=self.sell_exchange_id,
                                   buy_exchange_id=self.buy_exchange_id,
                                   pair_id=self.pair_id,
                                   deal_expire_timeout=self.deal_expire_timeout,
                                   cfg=self.cfg_file_name)

        return cmd
