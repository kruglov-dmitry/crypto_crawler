import argparse
import thread
import threading
from Queue import Queue as queue

from data_access.message_queue import get_message_queue
from data_access.priority_queue import get_priority_queue

from core.arbitrage_core import search_for_arbitrage, adjust_currency_balance, compute_new_min_cap_from_tickers
from core.expired_order import add_orders_to_watch_list
from data.BalanceState import dummy_balance_init

from dao.balance_utils import get_updated_balance_arbitrage
from dao.order_book_utils import get_order_book
from dao.ticker_utils import get_ticker_for_arbitrage
from dao.deal_utils import init_deals_with_logging_speedy
from dao.socket_utils import get_subcribtion_by_exchange, parse_update_by_exchanges, push_updates_to_queue

from data.ArbitrageConfig import ArbitrageConfig
from data.OrderBook import OrderBook

from data_access.classes.ConnectionPool import ConnectionPool
from data_access.memory_cache import get_cache
from data.MarketCap import MarketCap

from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_DEBUG, set_logging_level, \
    CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME, set_log_folder

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.exchange_utils import get_exchange_name_by_id
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from utils.time_utils import get_now_seconds_utc, sleep_for

from logging_tools.arbitrage_between_pair_logging import log_dont_supported_currency, log_balance_expired_errors

from constants import NO_MAX_CAP_LIMIT, BALANCE_EXPIRED_THRESHOLD

from deploy.classes.CommonSettings import CommonSettings


class ORDER_BOOK_SYNC_STAGES:
    BEFORE_SYNC = 1
    AFTER_SYNC = 2


class ArbitrageListener:
    def __init__(self, cfg, app_settings):

        self._init_settings(cfg)
        self._init_infrastructure(app_settings)
        self._init_arbitrage_state()

        self.subsribe_to_order_book_update()

        self.sync_order_books()

    def _init_settings(self, cfg):
        self.buy_exchange_id = cfg.buy_exchange_id
        self.sell_exchange_id = cfg.sell_exchange_id
        self.pair_id = cfg.pair_id
        self.log_file_name = cfg.log_file_name

        self.threshold = cfg.threshold
        self.reverse_threshold = cfg.reverse_threshold
        self.balance_threshold = cfg.balance_threshold

        self.cap_update_timeout = cfg.cap_update_timeout
        self.balance_update_timeout = cfg.balance_update_timeout

    def _init_infrastructure(self, app_settings):
        self.priority_queue = get_priority_queue(host=app_settings.cache_host, port=app_settings.cache_port)
        self.msg_queue = get_message_queue(host=app_settings.cache_host, port=app_settings.cache_port)
        self.local_cache = get_cache(host=app_settings.cache_host, port=app_settings.cache_port)
        self.processor = ConnectionPool(pool_size=2)

        self.sell_exchange_updates = queue()
        self.buy_exchange_updates = queue()

    def _init_arbitrage_state(self):
        self.init_deal_cap()
        self.init_balance_state()
        self.init_order_books()

        self.stage = ORDER_BOOK_SYNC_STAGES.BEFORE_SYNC

    def init_deal_cap(self):
        self.deal_cap = MarketCap(self.pair_id, get_now_seconds_utc())
        self.deal_cap.update_max_volume_cap(NO_MAX_CAP_LIMIT)
        self.subscribe_cap_update()

    def update_min_cap(self):
        cur_timest_sec = get_now_seconds_utc()
        tickers = get_ticker_for_arbitrage(self.pair_id, cur_timest_sec,
                                           [self.buy_exchange_id, self.sell_exchange_id], self.processor)
        new_cap = compute_new_min_cap_from_tickers(self.pair_id, tickers)

        if new_cap > 0:
            msg = "Updating old cap {op}".format(op=str(self.deal_cap))
            log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)

            self.deal_cap.update_min_volume_cap(new_cap, cur_timest_sec)

            msg = "New cap {op}".format(op=str(self.deal_cap))
            log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)

        else:
            msg = """CAN'T update minimum_volume_cap for {pair_id} at following
            exchanges: {exch1} {exch2}""".format(pair_id=self.pair_id,
                                                 exch1=get_exchange_name_by_id(self.buy_exchange_id),
                                                 exch2=get_exchange_name_by_id(self.sell_exchange_id))
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, self.log_file_name)

            log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)

    def init_balance_state(self):
        self.balance_state = dummy_balance_init(timest=0, default_volume=0, default_available_volume=0)
        self.subscribe_balance_update()

    def init_order_books(self):
        cur_timest_sec = get_now_seconds_utc()
        self.order_book_sell = OrderBook(pair_id=self.pair_id, timest=cur_timest_sec, sell_bids=[], buy_bids=[], exchange_id=self.sell_exchange_id)
        self.order_book_buy = OrderBook(pair_id=self.pair_id, timest=cur_timest_sec, sell_bids=[], buy_bids=[], exchange_id=self.buy_exchange_id)

    def update_from_queue(self, order_book, queue):
        while True:

            try:
                order_book_update = queue.get(block=False)
            except:
                order_book_update = None

            if order_book_update is None:
                break

            order_book.update(order_book_update)

            queue.task_done()

    def sync_order_books(self):

        self.order_book_sell = get_order_book(self.sell_exchange_id, self.pair_id)
        assert self.order_book_sell is not None
        self.order_book_sell.sort_by_price()
        self.update_from_queue(self.order_book_sell, self.sell_exchange_updates)

        print "Finishing syncing sell order book!"

        self.order_book_buy = get_order_book(self.buy_exchange_id, self.pair_id)
        assert self.order_book_buy is not None
        self.order_book_buy.sort_by_price()
        self.update_from_queue(self.order_book_buy, self.buy_exchange_updates)

        print "Finishing syncing buy order book!"

        self.stage = ORDER_BOOK_SYNC_STAGES.AFTER_SYNC

    def subscribe_cap_update(self):
        self.update_min_cap()
        threading.Timer(self.cap_update_timeout, self.subscribe_cap_update).start()

    def subscribe_balance_update(self):
        cur_timest_sec = get_now_seconds_utc()
        # self.balance_state = get_updated_balance_arbitrage(cfg, self.balance_state, self.local_cache)

        # if self.balance_state.expired(cur_timest_sec, self.buy_exchange_id, self.sell_exchange_id,
        #                               BALANCE_EXPIRED_THRESHOLD):
        #     log_balance_expired_errors(cfg, self.msg_queue, self.balance_state)

        #     assert False

        # threading.Timer(self.balance_update_timeout, self.subscribe_balance_update).start()

    def subsribe_to_order_book_update(self):
        # for both exchanges
        # Question 1 - selection of method for subscriptions
        # Question 2 - synchronisation of order book <<?>>

        buy_subscription_constructor = get_subcribtion_by_exchange(self.buy_exchange_id)
        sell_subscription_constructor = get_subcribtion_by_exchange(self.sell_exchange_id)

        buy_subscription = buy_subscription_constructor(self.pair_id, self.on_order_book_update, self.buy_exchange_updates)
        thread.start_new_thread(buy_subscription.subscribe, ())

        sell_subscription = sell_subscription_constructor(self.pair_id, self.on_order_book_update, self.sell_exchange_updates)
        thread.start_new_thread(sell_subscription.subscribe, ())

    def _print_top10_bids_asks(self, exchange_id):
        bids = self.order_book_sell.bid[:10]
        asks = self.order_book_sell.ask[:10]

        import os
        os.system('clear')

        print get_exchange_name_by_id(exchange_id)
        print "BIDS:"
        for b in bids:
            print b

        print "ASKS"
        for a in asks:
            print a

    def on_order_book_update(self, exchange_id, order_book_delta, exchange_updates, stage):
        # print "on_order_book_update for",  get_exchange_name_by_id(exchange_id), " thread_id: ",  thread.get_ident()
        # print exchange_id, order_book_delta

        order_book_updates = parse_update_by_exchanges(exchange_id, order_book_delta)

        if self.stage == ORDER_BOOK_SYNC_STAGES.BEFORE_SYNC:

            if exchange_id == self.buy_exchange_id:
                self.buy_exchange_updates.put(order_book_updates)
            else:
                self.sell_exchange_updates.put(order_book_updates)

            print "Syncing in progress ..."

        elif stage == ORDER_BOOK_SYNC_STAGES.AFTER_SYNC:
            if exchange_id == self.buy_exchange_id:
                self.order_book_buy.update(exchange_id, order_book_updates)
            else:
                self.order_book_sell.update(exchange_id, order_book_updates)

            self._print_top10_bids_asks(exchange_id)

        else:
            print "on_order_book_update: Unknown stage :("

        """
        for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:

            method = search_for_arbitrage if mode_id == DEAL_TYPE.ARBITRAGE else adjust_currency_balance
            active_threshold = self.threshold if mode_id == DEAL_TYPE.ARBITRAGE else self.reverse_threshold

            # FIXME NOTE: order book expiration check

            # init_deals_with_logging_speedy
            # FIXME NOTE: src dst vs buy sell
            status_code, deal_pair = method(self.order_book_src, self.order_book_dst, active_threshold,
                                            self.balance_threshold,
                                            init_deals_with_logging_speedy,
                                            self.balance_state, self.deal_cap,
                                            type_of_deal=mode_id, worker_pool=self.processor, msg_queue=self.msg_queue)

            add_orders_to_watch_list(deal_pair, self.priority_queue)

        self.deal_cap.update_max_volume_cap(NO_MAX_CAP_LIMIT)
        """


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

    results = parser.parse_args()

    cfg = ArbitrageConfig(results.sell_exchange_id, results.buy_exchange_id,
                          results.pair_id, results.threshold,
                          results.reverse_threshold, results.balance_threshold,
                          results.deal_expire_timeout,
                          results.cfg)

    app_settings = CommonSettings.from_cfg(results.cfg)

    set_logging_level(app_settings.logging_level_id)
    set_log_folder(app_settings.log_folder)
    load_keys(app_settings.key_path)

    # to avoid time-consuming check in future - validate arguments here
    for exchange_id in [results.sell_exchange_id, results.buy_exchange_id]:
        pair_name = get_currency_pair_name_by_exchange_id(cfg.pair_id, exchange_id)
        if pair_name is None:
            log_dont_supported_currency(cfg, exchange_id, cfg.pair_id)
            exit()

    ArbitrageListener(cfg, app_settings)
