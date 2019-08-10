import argparse
import threading
from Queue import Queue

from data_access.classes.connection_pool import ConnectionPool
from data_access.memory_cache import get_cache
from data_access.message_queue import get_message_queue
from data_access.priority_queue import get_priority_queue

from core.arbitrage_core import update_min_cap, search_for_arbitrage
from core.expired_order import add_orders_to_watch_list

from dao.deal_utils import init_deals_with_logging_speedy
from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_book
from dao.socket_utils import get_subcribtion_by_exchange

from data.arbitrage_config import ArbitrageConfig
from data.order_book import OrderBook

from debug_utils import print_to_console, LOG_ALL_ERRORS, set_logging_level, \
    set_log_folder, SOCKET_ERRORS_LOG_FILE_NAME

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from enums.status import STATUS
from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.exchange_utils import get_exchange_name_by_id
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for, get_now_seconds_utc_ms
from utils.system_utils import die_hard

from logging_tools.arbitrage_between_pair_logging import log_dont_supported_currency, log_balance_expired_errors, \
    log_reset_stage_successfully, log_init_reset, log_reset_final_stage, log_cant_update_volume_cap, \
    log_finishing_syncing_order_book, log_all_order_book_synced, log_order_book_update_failed_pre_sync, \
    log_order_book_update_failed_post_sync, log_one_of_subscriptions_failed

from constants import NO_MAX_CAP_LIMIT, BALANCE_EXPIRED_THRESHOLD, YES_I_KNOW_WHAT_AM_I_DOING

from deploy.classes.common_settings import CommonSettings

from services.sync_stage import get_stage, set_stage
from services.arbitrage_wrapper import ArbitrageWrapper
from services.live_updates import _print_top10


class ArbitrageListener(ArbitrageWrapper):
    def __init__(self, cfg, app_settings):

        ArbitrageWrapper.__init__(self, cfg)

        self._init_infrastructure(app_settings)

    def start(self):
        self.reset_arbitrage_state()
        while True:
            if self.buy_subscription.is_running() and self.sell_subscription.is_running():
                sleep_for(1)
            else:
                # We will NOT issue a reset till any pending process still running
                while self.buy_subscription.is_running() or self.sell_subscription.is_running():
                    sleep_for(1)
                self.reset_arbitrage_state()

    def reset_arbitrage_state(self):

        local_timeout = 1

        while True:
            sleep_for(local_timeout)

            log_init_reset()

            set_stage(ORDER_BOOK_SYNC_STAGES.RESETTING)

            self.update_balance_run_flag = False
            self.update_min_cap_run_flag = False

            self.clear_queue(self.sell_exchange_updates)
            self.clear_queue(self.buy_exchange_updates)

            self._init_arbitrage_state()            # Spawn balance & cap threads, no blocking
            self.subscribe_to_order_book_update()   # Spawn order book subscription threads, no blocking
            self.sync_order_books()                 # Spawn order book sync threads, BLOCKING till they finished

            log_reset_final_stage()

            if get_stage() != ORDER_BOOK_SYNC_STAGES.AFTER_SYNC:

                self.shutdown_subscriptions()

                log_to_file("reset_arbitrage_state - cant sync order book, lets try one more time!", SOCKET_ERRORS_LOG_FILE_NAME)

                while self.buy_subscription.is_running() or self.sell_subscription.is_running():
                    sleep_for(1)

                local_timeout += 1

            else:
                break

        log_reset_stage_successfully()

    def _init_infrastructure(self, app_settings):
        self.priority_queue = get_priority_queue(host=app_settings.cache_host, port=app_settings.cache_port)
        self.msg_queue = get_message_queue(host=app_settings.cache_host, port=app_settings.cache_port)
        self.local_cache = get_cache(host=app_settings.cache_host, port=app_settings.cache_port)
        self.processor = ConnectionPool(pool_size=2)

        self.sell_exchange_updates = Queue()
        self.buy_exchange_updates = Queue()

        buy_subscription_constructor = get_subcribtion_by_exchange(self.buy_exchange_id)
        sell_subscription_constructor = get_subcribtion_by_exchange(self.sell_exchange_id)

        self.buy_subscription = buy_subscription_constructor(self.pair_id, on_update=self.on_order_book_update)
        self.sell_subscription = sell_subscription_constructor(self.pair_id, on_update=self.on_order_book_update)

    def _init_arbitrage_state(self):
        self.init_deal_cap()
        self.init_balance_state()
        self.init_order_books()

        self.sell_order_book_synced = False
        self.buy_order_book_synced = False

        set_stage(ORDER_BOOK_SYNC_STAGES.BEFORE_SYNC)

    def init_deal_cap(self):
        self.update_min_cap_run_flag = True
        # TODO FIXME UNCOMMENT self.subscribe_cap_update()

    def update_min_cap(self):
        log_to_file("Subscribing for updating cap updates", SOCKET_ERRORS_LOG_FILE_NAME)
        while self.update_min_cap_run_flag:
            update_min_cap(self.cfg, self.deal_cap, self.processor)

            for _ in xrange(self.cap_update_timeout):
                if self.update_min_cap_run_flag:
                    sleep_for(1)

        log_to_file("Exit from updating cap updates", SOCKET_ERRORS_LOG_FILE_NAME)

    def init_balance_state(self):
        self.update_balance_run_flag = True
        # TODO FIXME UNCOMMENT self.subscribe_balance_update()

    def init_order_books(self):
        cur_timest_sec = get_now_seconds_utc()
        self.order_book_sell = OrderBook(self.pair_id, cur_timest_sec, sell_bids=[], buy_bids=[], exchange_id=self.sell_exchange_id)
        self.order_book_buy = OrderBook(self.pair_id, cur_timest_sec, sell_bids=[], buy_bids=[], exchange_id=self.buy_exchange_id)

    def update_from_queue(self, exchange_id, order_book, queue):
        while True:

            if not self.buy_subscription.is_running() or not self.sell_subscription.is_running():
                return STATUS.FAILURE

            try:
                order_book_update = queue.get(block=False)
            except:
                order_book_update = None

            if order_book_update is None:
                break

            if STATUS.SUCCESS != order_book.update(exchange_id, order_book_update):
                return STATUS.FAILURE

            queue.task_done()

        return STATUS.SUCCESS

    @classmethod
    def clear_queue(cls, m_queue):
        while True:

            try:
                order_book_update = m_queue.get(block=False)
            except:
                order_book_update = None

            if order_book_update is None:
                break

            m_queue.task_done()

    def sync_sell_order_book(self):
        if self.sell_exchange_id in [EXCHANGE.BINANCE, EXCHANGE.BITTREX]:
            self.order_book_sell = get_order_book(self.sell_exchange_id, self.pair_id)

            if self.order_book_sell is None:
                return

            self.order_book_sell.sort_by_price()

            if STATUS.FAILURE == self.update_from_queue(self.sell_exchange_id, self.order_book_sell, self.sell_exchange_updates):
                self.sell_order_book_synced = False

                return

        log_finishing_syncing_order_book("SELL")

        self.sell_order_book_synced = True

    def sync_buy_order_book(self):
        if self.buy_exchange_id in [EXCHANGE.BINANCE, EXCHANGE.BITTREX]:
            self.order_book_buy = get_order_book(self.buy_exchange_id, self.pair_id)

            if self.order_book_buy is None:
                return

            self.order_book_buy.sort_by_price()

            if STATUS.FAILURE == self.update_from_queue(self.buy_exchange_id, self.order_book_buy, self.buy_exchange_updates):
                self.buy_order_book_synced = False
                return

        log_finishing_syncing_order_book("BUY")

        self.buy_order_book_synced = True

    def sync_order_books(self):

        # DK NOTE: Those guys will endup by themselves

        msg = "sync_order_books - stage status is {}".format(get_stage())
        log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)

        sync_sell_order_book_thread = self.start_process_daemon(self.sync_sell_order_book, args=())
        sync_buy_order_book_thread = self.start_process_daemon(self.sync_buy_order_book, args=())

        # Wait for both thread be finished
        sync_sell_order_book_thread.join()
        sync_buy_order_book_thread.join()

        if self.sell_order_book_synced and self.buy_order_book_synced:
            set_stage(ORDER_BOOK_SYNC_STAGES.AFTER_SYNC)

        log_all_order_book_synced()

    def subscribe_cap_update(self):
        self.start_process_daemon(self.update_min_cap, args=())

    def update_balance(self):

        while self.update_balance_run_flag:
            cur_timest_sec = get_now_seconds_utc()
            self.balance_state = get_updated_balance_arbitrage(cfg, self.balance_state, self.local_cache)

            if self.balance_state.expired(cur_timest_sec, self.buy_exchange_id, self.sell_exchange_id,
                                          BALANCE_EXPIRED_THRESHOLD):
                log_balance_expired_errors(cfg, self.msg_queue, self.balance_state)

                assert False

            sleep_for(self.balance_update_timeout)

    def subscribe_balance_update(self):
        self.start_process_daemon(self.update_balance, args=())

    @staticmethod
    def start_process_daemon(method, args):
        new_thread = threading.Thread(target=method, args=args)
        new_thread.daemon = True
        new_thread.start()
        return new_thread

    def subscribe_to_order_book_update(self):
        self.start_process_daemon(self.buy_subscription.subscribe, args=())
        self.start_process_daemon(self.sell_subscription.subscribe, args=())

    def shutdown_subscriptions(self):
        self.sell_subscription.disconnect()
        self.buy_subscription.disconnect()

    def on_order_book_update(self, exchange_id, order_book_updates):
        """
        :param exchange_id:
        :param order_book_updates:  parsed OrderBook or OrderBookUpdates according to exchange specs
        :param stage:               whether BOTH orderbook synced or NOT
        :return:
        """

        exchange_name = get_exchange_name_by_id(exchange_id)

        print_to_console("Got update for {exch} Current number of threads: {thr_num}"
                         .format(exch=exchange_name, thr_num=threading.active_count()), LOG_ALL_ERRORS)

        current_stage = get_stage()

        if not self.buy_subscription.is_running() or not self.sell_subscription.is_running():

            log_one_of_subscriptions_failed(self.buy_subscription.is_running(), self.sell_subscription.is_running(), current_stage)

            self.shutdown_subscriptions()

            return

        if order_book_updates is None:
            print_to_console("Order book update is NONE! for {}".format(exchange_name), LOG_ALL_ERRORS)
            return

        if current_stage == ORDER_BOOK_SYNC_STAGES.BEFORE_SYNC:
            print_to_console("Syncing in progress ...", LOG_ALL_ERRORS)

            if exchange_id == self.buy_exchange_id:
                if self.buy_order_book_synced:
                    order_book_update_status = self.order_book_buy.update(exchange_id, order_book_updates)
                    if order_book_update_status == STATUS.FAILURE:

                        log_order_book_update_failed_pre_sync("BUY", exchange_id, order_book_updates)

                        self.shutdown_subscriptions()

                else:
                    self.buy_exchange_updates.put(order_book_updates)
            else:
                if self.sell_order_book_synced:
                    order_book_update_status = self.order_book_sell.update(exchange_id, order_book_updates)
                    if order_book_update_status == STATUS.FAILURE:

                        log_order_book_update_failed_pre_sync("SELL", exchange_id, order_book_updates)

                        self.shutdown_subscriptions()

                else:
                    self.sell_exchange_updates.put(order_book_updates)

        elif current_stage == ORDER_BOOK_SYNC_STAGES.AFTER_SYNC:

            print_to_console("Update after syncing... {}".format(exchange_name), LOG_ALL_ERRORS)

            if exchange_id == self.buy_exchange_id:
                order_book_update_status = self.order_book_buy.update(exchange_id, order_book_updates)
                if order_book_update_status == STATUS.FAILURE:

                    log_order_book_update_failed_post_sync(exchange_id, order_book_updates)

                    self.shutdown_subscriptions()

                    return

            else:
                order_book_update_status = self.order_book_sell.update(exchange_id, order_book_updates)
                if order_book_update_status == STATUS.FAILURE:

                    log_order_book_update_failed_post_sync(exchange_id, order_book_updates)

                    self.shutdown_subscriptions()

                    return

            _print_top10(exchange_id, self.order_book_buy, self.order_book_sell)

            if not YES_I_KNOW_WHAT_AM_I_DOING:
                die_hard("LIVE TRADING!")

            # DK NOTE: only at this stage we are ready for searching for arbitrage

            # for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:
            #   method = search_for_arbitrage if mode_id == DEAL_TYPE.ARBITRAGE else adjust_currency_balance
            #   active_threshold = self.threshold if mode_id == DEAL_TYPE.ARBITRAGE else self.reverse_threshold
            # FIXME NOTE: order book expiration check
            # FIXME NOTE: src dst vs buy sell
            ts1 = get_now_seconds_utc_ms()
            status_code, deal_pair = search_for_arbitrage(self.order_book_sell, self.order_book_buy,
                                                          self.threshold,
                                                          self.balance_threshold,
                                                          init_deals_with_logging_speedy,
                                                          self.balance_state, self.deal_cap,
                                                          type_of_deal=DEAL_TYPE.ARBITRAGE,
                                                          worker_pool=self.processor,
                                                          msg_queue=self.msg_queue)

            ts2 = get_now_seconds_utc_ms()

            msg = "Start: {ts1} ms End: {ts2} ms Runtime: {d} ms".format(ts1=ts1, ts2=ts2, d=ts2-ts1)

            #
            #               FIXME
            #
            #   Yeah, we write to disk after every trade
            #   Yeah, it is not really about speed :(
            #
            log_to_file(msg, "profile.txt")
            add_orders_to_watch_list(deal_pair, self.priority_queue)
            self.deal_cap.update_max_volume_cap(NO_MAX_CAP_LIMIT)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Constantly poll two exchange for order book for particular pair "
                                                 "and initiate sell\\buy deals for arbitrage opportunities")

    parser.add_argument('--threshold', action="store", type=float, required=True)
    parser.add_argument('--balance_threshold', action="store", type=float, required=True)
    parser.add_argument('--reverse_threshold', action="store", type=float, required=True)
    parser.add_argument('--sell_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--buy_exchange_id', action="store", type=int, required=True)
    parser.add_argument('--pair_id', action="store", type=int, required=True)
    parser.add_argument('--deal_expire_timeout', action="store", type=int, required=True)

    parser.add_argument('--cfg', action="store", required=True)

    arguments = parser.parse_args()

    cfg = ArbitrageConfig.from_args(arguments)

    app_settings = CommonSettings.from_cfg(cfg)

    set_logging_level(app_settings.logging_level_id)
    set_log_folder(app_settings.log_folder)
    load_keys(app_settings.key_path)

    # to avoid time-consuming check in future - validate arguments here
    for exchange_id in [cfg.sell_exchange_id, cfg.buy_exchange_id]:
        pair_name = get_currency_pair_name_by_exchange_id(cfg.pair_id, exchange_id)
        if pair_name is None:
            log_dont_supported_currency(cfg, exchange_id, cfg.pair_id)
            exit()

    ArbitrageListener(cfg, app_settings).start()
