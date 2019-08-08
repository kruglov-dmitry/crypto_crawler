from constants import NO_MAX_CAP_LIMIT

from data.market_cap import MarketCap
from data.balance_state import dummy_balance_init

from utils.time_utils import get_now_seconds_utc


class ArbitrageWrapper(object):
    def __init__(self, cfg):
        self.cfg = cfg

        self.update_balance_run_flag = False
        self.update_min_cap_run_flag = False

        self.deal_cap = MarketCap(self.pair_id, get_now_seconds_utc())
        self.deal_cap.update_max_volume_cap(NO_MAX_CAP_LIMIT)
        self.update_min_cap_run_flag = False

        self.balance_state = dummy_balance_init(timest=0,
                                                default_volume=100500,
                                                default_available_volume=100500)
        self.update_balance_run_flag = False

        self.order_book_buy = None
        self.buy_order_book_synced = False

        self.order_book_sell = None
        self.sell_order_book_synced = False

    @property
    def buy_exchange_id(self):
        return self.cfg.buy_exchange_id

    @property
    def sell_exchange_id(self):
        return self.cfg.sell_exchange_id

    @property
    def pair_id(self):
        return self.cfg.pair_id

    @property
    def log_file_name(self):
        return self.cfg.log_file_name

    @property
    def threshold(self):
        return self.cfg.threshold

    @property
    def reverse_threshold(self):
        return self.cfg.reverse_threshold

    @property
    def balance_threshold(self):
        return self.cfg.balance_threshold

    @property
    def cap_update_timeout(self):
        return self.cfg.cap_update_timeout

    @property
    def balance_update_timeout(self):
        return self.cfg.balance_update_timeout
