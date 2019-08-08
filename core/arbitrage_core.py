from decimal import Decimal

from debug_utils import should_print_debug, ERROR_LOG_FILE_NAME, print_to_console, \
    LOG_ALL_ERRORS, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME

from utils.time_utils import get_now_seconds_utc
from utils.currency_utils import split_currency_pairs
from utils.file_utils import log_to_file
from utils.string_utils import truncate_float
from utils.exchange_utils import get_exchange_name_by_id

from core.base_analysis import get_change

from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE
from enums.status import STATUS

from data.trade import Trade
from data.trade_pair import TradePair

from data_access.memory_cache import get_next_arbitrage_id
from data_access.message_queue import ORDERS_MSG, FAILED_ORDERS_MSG
from data_access.priority_queue import ORDERS_EXPIRE_MSG

from binance.precision_by_currency import round_volume_by_binance_rules
from huobi.precision_by_currency import round_volume_by_huobi_rules

from constants import FIRST, LAST, NO_MAX_CAP_LIMIT, MIN_VOLUME_COEFFICIENT, MAX_VOLUME_COEFFICIENT, DECIMAL_ZERO

from dao.dao import parse_order_id
from dao.deal_utils import init_deal
from dao.ticker_utils import get_ticker_for_arbitrage


from logging_tools.arbitrage_core_logging import log_arbitrage_heart_beat, log_arbitrage_determined_volume_not_enough, \
    log_currency_disbalance_present, log_currency_disbalance_heart_beat, log_arbitrage_determined_price_not_enough
from logging_tools.arbitrage_between_pair_logging import log_dublicative_order_book
from logging_tools.expired_order_logging import log_placing_new_deal, log_cant_placing_new_deal, log_too_small_volume, \
    log_expired_order_replacement_result


# FIXME NOTES:
# 1. load current deals set?
# 2. integrate to bot commands to show active deal and be able to cancel them by command in chat?


def search_for_arbitrage(sell_order_book, buy_order_book, threshold, balance_threshold,
                         action_to_perform,
                         balance_state, deal_cap,
                         type_of_deal,
                         worker_pool, msg_queue):
    """
    :param sell_order_book:         order_book from exchange where we are going to SELL
    :param buy_order_book:          order_book from exchange where we are going to BUY
    :param threshold:               difference in price in percent that MAY trigger MUTUAL deal placement
    :param balance_threshold:       for interface compatibility with balance_adjustment method
    :param action_to_perform:       method that will be called in case threshold condition are met
    :param balance_state:           balance across all active exchange for all supported currencies
    :param deal_cap:                dynamically updated minimum volume per currency
    :param type_of_deal:            ARBITRAGE or REVERSE. EXPIRED or FAILED will not be processed here
    :param worker_pool:             gevent based connection pool for speedy deal placement
    :param msg_queue:               redis backed msq queue with notification for Telegram
    :return:
    """

    deal_status = STATUS.FAILURE, None

    if not sell_order_book.bid or not buy_order_book.ask:
        return deal_status

    difference = get_change(sell_order_book.bid[FIRST].price, buy_order_book.ask[LAST].price, provide_abs=False)

    if should_print_debug():
        log_arbitrage_heart_beat(sell_order_book, buy_order_book, difference)

    if difference >= threshold:
        min_volume = determine_minimum_volume(sell_order_book, buy_order_book, balance_state)

        min_volume = adjust_minimum_volume_by_trading_cap(deal_cap, min_volume)

        min_volume = adjust_maximum_volume_by_trading_cap(deal_cap, min_volume)

        min_volume = round_volume_by_exchange_rules(sell_order_book.exchange_id, buy_order_book.exchange_id,
                                                    min_volume, sell_order_book.pair_id)

        if min_volume <= 0:
            log_arbitrage_determined_volume_not_enough(sell_order_book, buy_order_book, msg_queue)
            return deal_status

        sell_price = adjust_price_by_order_book(sell_order_book.bid, min_volume)

        arbitrage_id = get_next_arbitrage_id()
        create_time = get_now_seconds_utc()
        trade_at_first_exchange = Trade(DEAL_TYPE.SELL, sell_order_book.exchange_id, sell_order_book.pair_id,
                                        sell_price, min_volume, sell_order_book.timest,
                                        create_time, arbitrage_id=arbitrage_id)

        buy_price = adjust_price_by_order_book(buy_order_book.ask, min_volume)
        trade_at_second_exchange = Trade(DEAL_TYPE.BUY, buy_order_book.exchange_id, buy_order_book.pair_id,
                                         buy_price, min_volume, buy_order_book.timest,
                                         create_time, arbitrage_id=arbitrage_id)

        final_difference = get_change(sell_price, buy_price, provide_abs=False)
        if final_difference <= 0.2:
            log_arbitrage_determined_price_not_enough(sell_price, sell_order_book.bid[FIRST].price,
                                                      buy_price, buy_order_book.ask[LAST].price,
                                                      difference, final_difference,
                                                      sell_order_book.pair_id, msg_queue)
            return deal_status

        trade_pair = TradePair(trade_at_first_exchange, trade_at_second_exchange, sell_order_book.timest,
                               buy_order_book.timest, type_of_deal)

        placement_status = action_to_perform(trade_pair, final_difference, "history_trades.log", worker_pool, msg_queue)

        # NOTE: if we can't update balance for more than TIMEOUT seconds arbitrage process will exit
        # for exchange_id in [trade_pair.deal_1.exchange_id, trade_pair.deal_2.exchange_id]:
        #     update_balance_by_exchange(exchange_id)

        # deal_status = placement_status, trade_pair

    return deal_status


def is_no_pending_order(currency_id, src_exchange_id, dst_exchange_id):
    # FIXME - have to load active deals per exchange >_<
    # 02.05.2018 issue 65 ?
    return True


def determine_minimum_volume(first_order_book, second_order_book, balance_state):
    """
        we are going to SELL something at first exchange
        we are going to BUY something at second exchange using BASE_CURRENCY

        This method determine maximum available volume of DST_CURRENCY on 1ST exchanges
        This method determine maximum available volume according to amount of available BASE_CURRENCY on 2ND exchanges

    :param first_order_book:
    :param second_order_book:
    :param balance_state:
    :return:    Decimal object representing exact number
    """

    # 1st stage: What is minimum amount of volume according to order book
    min_volume = min(first_order_book.bid[FIRST].volume, second_order_book.ask[LAST].volume)
    if min_volume <= 0:
        msg = "determine_minimum_volume - something severely wrong - NEGATIVE min price: {pr}".format(pr=min_volume)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

        assert min_volume <= 0

    base_currency_id, dst_currency_id = split_currency_pairs(first_order_book.pair_id)

    # 2nd stage: What is maximum volume we can SELL at first exchange
    if not balance_state.do_we_have_enough(dst_currency_id,
                                           first_order_book.exchange_id,
                                           min_volume):
        min_volume = balance_state.get_available_volume_by_currency(dst_currency_id, first_order_book.exchange_id)

    # 3rd stage: what is maximum volume we can buy
    if not balance_state.do_we_have_enough_by_pair(first_order_book.pair_id,
                                                   second_order_book.exchange_id,
                                                   min_volume,
                                                   second_order_book.ask[LAST].price):
        min_volume = (MAX_VOLUME_COEFFICIENT * balance_state.get_available_volume_by_currency(
            base_currency_id, second_order_book.exchange_id)) / second_order_book.ask[LAST].price

    return min_volume


def determine_maximum_volume_by_balance(pair_id, deal_type, volume, price, balance):
    """
    :param pair_id:
    :param deal_type:
    :param volume:
    :param price:
    :param balance:
    :return: Decimal object representing exact volume
    """

    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if deal_type == DEAL_TYPE.SELL:
        # What is maximum volume we can SELL at exchange
        if not balance.do_we_have_enough(dst_currency_id, volume):
            volume = balance.available_balance[dst_currency_id]
    elif deal_type == DEAL_TYPE.BUY:
        # what is maximum volume we can buy at exchange
        if not balance.do_we_have_enough(base_currency_id, volume * price):
            volume = (MAX_VOLUME_COEFFICIENT * balance.available_balance[base_currency_id]) / price
    else:

        assert deal_type not in [DEAL_TYPE.BUY, DEAL_TYPE.SELL]

    return volume


def adjust_minimum_volume_by_trading_cap(deal_cap, min_volume):
    if min_volume < deal_cap.get_min_volume_cap():
        min_volume = -1  # Yeap, no need to even bother

    return min_volume


def adjust_maximum_volume_by_trading_cap(deal_cap, volume):

    if deal_cap.get_max_volume_cap() == NO_MAX_CAP_LIMIT:
        # so we treat it as no max cap
        return volume

    if volume > deal_cap.get_max_volume_cap():
        return deal_cap.get_max_volume_cap()

    return volume


def round_volume_by_exchange_rules(sell_exchange_id, buy_exchange_id, min_volume, pair_id):
    if EXCHANGE.BINANCE in {sell_exchange_id, buy_exchange_id}:
        return round_volume_by_binance_rules(volume=min_volume, pair_id=pair_id)
    elif EXCHANGE.HUOBI in {sell_exchange_id, buy_exchange_id}:
        return round_volume_by_huobi_rules(volume=min_volume, pair_id=pair_id)

    return truncate_float(min_volume, 8)


def round_volume(exchange_id, min_volume, pair_id):
    if exchange_id == EXCHANGE.BINANCE:
        return round_volume_by_binance_rules(volume=min_volume, pair_id=pair_id)
    elif exchange_id == EXCHANGE.HUOBI:
        return round_volume_by_huobi_rules(volume=min_volume, pair_id=pair_id)

    return truncate_float(min_volume, 8)


def adjust_price_by_order_book(orders, min_volume):
    """
        In order to address not immediate speed and influence of other participant of market
        We will use not the best price from order book to minimise number of non-closed deals
        Details and discussion at https://gitlab.com/crypto_trade/crypto_crawler/issues/15

        In short dive into order book, take price from level where we can place min_volume * 2

    :param orders: the most recent order book
    :param min_volume: Decimal value of volume determined according to various checks
    :return: Decimal object with exact price
    """
    new_price = Decimal(-10.0)
    acc_volume = Decimal(0.0)
    max_volume = 2 * min_volume
    max_len = len(orders)

    if min_volume == 0.0:
        msg = "adjust_price_by_order_book: ERROR min volume is ZERO"
        log_to_file(msg, "price_adjustment.log")

        assert min_volume == 0

    idx = 0
    while acc_volume < max_volume and idx < max_len:
        new_price = orders[idx].price
        acc_volume += orders[idx].volume
        idx += 1

    # FIXME SLOW DEBUG
    # msg = "Order book:\n"
    # for o in orders:
    #     msg += str(o) + "\n"
    # msg += "res_price: " + str(new_price)
    # log_to_file(msg, "price_adjustment.log")

    return new_price


def adjust_currency_balance(first_order_book, second_order_book, threshold, balance_threshold,
                            action_to_perform,
                            balance_state, deal_cap,
                            type_of_deal,
                            worker_pool, msg_queue):
    deal_status = STATUS.FAILURE, None

    pair_id = first_order_book.pair_id
    src_currency_id, dst_currency_id = split_currency_pairs(pair_id)
    src_exchange_id = first_order_book.exchange_id
    dst_exchange_id = second_order_book.exchange_id

    if balance_state.is_there_disbalance(dst_currency_id, src_exchange_id, dst_exchange_id, balance_threshold) and \
            is_no_pending_order(pair_id, src_exchange_id, dst_exchange_id):

        max_volume = Decimal(0.5) * abs(balance_state.get_available_volume_by_currency(
            dst_currency_id, dst_exchange_id) - balance_state.get_available_volume_by_currency(
            dst_currency_id, src_exchange_id))

        # FIXME NOTE: side effect here
        deal_cap.update_max_volume_cap(max_volume)

        log_currency_disbalance_present(src_exchange_id, dst_exchange_id, pair_id, dst_currency_id,
                                        balance_threshold, max_volume, threshold)

        deal_status = search_for_arbitrage(first_order_book, second_order_book, threshold, balance_threshold,
                                           action_to_perform, balance_state, deal_cap,
                                           type_of_deal, worker_pool, msg_queue)
    else:
        log_currency_disbalance_heart_beat(src_exchange_id, dst_exchange_id, dst_currency_id, balance_threshold)

    return deal_status


def compute_new_min_cap_from_tickers(pair_id, tickers):
    min_price = DECIMAL_ZERO

    for ticker in tickers:
        if ticker is not None:
            try:
                # FIXME NOTE:   in case of errors we may get string with error instead of Ticker object
                #               need to fix process_async_to_list at ConnectionPool
                min_price = max(min_price, ticker.ask)
            except:
                msg = "Msg bad ticker value = {}!".format(ticker)
                log_to_file(msg, ERROR_LOG_FILE_NAME)

    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if min_price != DECIMAL_ZERO:
        return MIN_VOLUME_COEFFICIENT[base_currency_id] / min_price

    return DECIMAL_ZERO


def compute_min_cap_from_ticker(pair_id, ticker):
    min_price = DECIMAL_ZERO

    if ticker is not None:
        min_price = max(min_price, ticker.ask)

    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if min_price != DECIMAL_ZERO:
        return MIN_VOLUME_COEFFICIENT[base_currency_id] / min_price

    return DECIMAL_ZERO


def place_order_by_market_rate(expired_order, msg_queue, priority_queue, min_volume, balance, order_book, log_file_name):
    max_volume = determine_maximum_volume_by_balance(expired_order.pair_id, expired_order.trade_type,
                                                     expired_order.volume, expired_order.price, balance)

    max_volume = round_volume(expired_order.exchange_id, max_volume, expired_order.pair_id)

    if max_volume < min_volume:

        log_too_small_volume(expired_order, max_volume, min_volume, msg_queue)

        return

    expired_order.volume = max_volume
    expired_order.create_time = get_now_seconds_utc()

    msg = "Replace EXPIRED order with new one - {tt}".format(tt=expired_order)
    err_code, json_document = init_deal(expired_order, msg)

    log_expired_order_replacement_result(expired_order, json_document, msg_queue)

    if err_code == STATUS.SUCCESS:

        expired_order.execute_time = get_now_seconds_utc()
        expired_order.order_book_time = long(order_book.timest)
        expired_order.order_id = parse_order_id(expired_order.exchange_id, json_document)

        msg_queue.add_order(ORDERS_MSG, expired_order)

        priority_queue.add_order_to_watch_queue(ORDERS_EXPIRE_MSG, expired_order)

        log_placing_new_deal(expired_order, msg_queue, log_file_name)
    else:
        log_cant_placing_new_deal(expired_order, msg_queue)

        msg_queue.add_order(FAILED_ORDERS_MSG, expired_order, log_file_name)


#
#       Routines below used in first version of arbitrage - via REST processing only
#


def update_min_cap(cfg, deal_cap, processor):
    cur_timest_sec = get_now_seconds_utc()
    tickers = get_ticker_for_arbitrage(cfg.pair_id, cur_timest_sec,
                                       [cfg.buy_exchange_id, cfg.sell_exchange_id], processor)
    new_cap = compute_new_min_cap_from_tickers(cfg.pair_id, tickers)

    if new_cap > 0:
        msg = "Updating old cap {op}".format(op=deal_cap)
        log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)

        deal_cap.update_min_volume_cap(new_cap, cur_timest_sec)

        msg = "New cap {op}".format(op=deal_cap)
        log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)

    else:
        msg = """CAN'T update minimum_volume_cap for {pair_id} at following
        exchanges: {exch1} {exch2}""".format(pair_id=cfg.pair_id, exch1=get_exchange_name_by_id(cfg.buy_exchange_id),
                                             exch2=get_exchange_name_by_id(cfg.sell_exchange_id))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, cfg.log_file_name)

        log_to_file(msg, CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME)


def is_order_books_expired(order_book_src, order_book_dst, local_cache, msg_queue, log_file_name):

    for order_book in [order_book_src, order_book_dst]:
        prev_order_book = local_cache.get_last_order_book(order_book.pair_id, order_book.exchange_id)

        if prev_order_book is None:
            continue

        total_asks = len(order_book.ask)
        number_of_same_asks = len(set(order_book.ask).intersection(prev_order_book.ask))

        total_bids = len(order_book.bid)
        number_of_same_bids = len(set(order_book.bid).intersection(prev_order_book.bid))

        if total_asks == number_of_same_asks or total_bids == number_of_same_bids:
            # FIXME NOTE: probably we can loose a bit this condition - for example check that order book
            # should differ for more than 10% of bids OR asks ?
            log_dublicative_order_book(log_file_name, order_book, prev_order_book, msg_queue)
            return True

    return False