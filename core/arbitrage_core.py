import sys

sys.setrecursionlimit(10000)

from debug_utils import should_print_debug, print_to_console, LOG_ALL_ERRORS, ERROR_LOG_FILE_NAME

from utils.time_utils import get_now_seconds_utc
from utils.currency_utils import split_currency_pairs
from utils.file_utils import log_to_file

from core.base_analysis import get_change

from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE
from enums.status import STATUS

from data.Trade import Trade
from data.TradePair import TradePair

from data_access.memory_cache import get_next_arbitrage_id

from binance.precision_by_currency import round_volume_by_binance_rules
from constants import FIRST, LAST, NO_MAX_CAP_LIMIT, MIN_VOLUME_COEFFICIENT, MAX_VOLUME_COEFFICIENT

from logging_tools.arbitrage_core_logging import log_arbitrage_heart_beat, log_arbitrage_determined_volume_not_enough, \
    log_currency_disbalance_present, log_currency_disbalance_heart_beat, log_arbitrage_determined_price_not_enough

from dao.balance_utils import update_balance_by_exchange


# FIXME NOTES:
# 1. load current deals set?
# 2. integrate to bot commands to show active deal and be able to cancel them by command in chat?
# 3. take into account that we may need to change frequency of polling based on prospectivness of currency pair


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
    :param balance_state:           balance accross all active exchange for all supported currencies
    :param deal_cap:                dynamically updated minimum volume per currency
    :param type_of_deal:            ARBITRAGE\REVERSE. EXPIRED will not be processed here
    :param worker_pool:             gevent based connection pool for speedy deal placement
    :param msg_queue:               redis backed msq queue with notificaion for Telegram
    :return:
    """

    deal_status = STATUS.FAILURE, None

    if len(sell_order_book.bid) == 0 or len(buy_order_book.ask) == 0:
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
        for exchange_id in [trade_pair.deal_1.exchange_id, trade_pair.deal_2.exchange_id]:
            update_balance_by_exchange(exchange_id)

        deal_status = placement_status, trade_pair

    return deal_status


def is_no_pending_order(currency_id, src_exchange_id, dst_exchange_id):
    # FIXME - have to load active deals per exchange >_<
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
    :return:
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
        min_volume = ( MAX_VOLUME_COEFFICIENT * balance_state.get_available_volume_by_currency(
            base_currency_id, second_order_book.exchange_id)) / float(second_order_book.ask[LAST].price)

    return min_volume


def determine_maximum_volume_by_balance(pair_id, deal_type, volume, price, balance):
    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if deal_type == DEAL_TYPE.SELL:
        # What is maximum volume we can SELL at exchange
        if not balance.do_we_have_enough(dst_currency_id, volume):
            volume = balance.available_balance[dst_currency_id]
    elif deal_type == DEAL_TYPE.BUY:
        # what is maximum volume we can buy at exchange
        if not balance.do_we_have_enough(base_currency_id, volume * price):
            volume = (MAX_VOLUME_COEFFICIENT * balance.available_balance[base_currency_id]) / float(price)
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
    if sell_exchange_id == EXCHANGE.BINANCE or buy_exchange_id == EXCHANGE.BINANCE:
        return round_volume_by_binance_rules(volume=min_volume, pair_id=pair_id)
    return min_volume


def round_volume(exchange_id, min_volume, pair_id):
    if exchange_id == EXCHANGE.BINANCE:
        return round_volume_by_binance_rules(volume=min_volume, pair_id=pair_id)

    return min_volume


def adjust_price_by_order_book(orders, min_volume):
    """
        In order to address not immediate speed and influence of other participant of market
        We will use not the best price from order book to minimise number of non-closed deals
        Details and discussion at https://gitlab.com/crypto_trade/crypto_crawler/issues/15

        In short dive into order book, take price from level where we can place min_volume * 2

    :param orders: the most recent order book
    :param min_volume: volume determined according to various check
    :return:
    """
    new_price = -10.0
    acc_volume = 0.0
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

    msg = "Order book:\n"
    for o in orders:
        msg += str(o) + "\n"
    msg += "res_price: " + str(new_price)
    log_to_file(msg, "price_adjustment.log")

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

        max_volume = 0.5 * abs(balance_state.get_available_volume_by_currency(dst_currency_id, dst_exchange_id) -
                            balance_state.get_available_volume_by_currency(dst_currency_id, src_exchange_id))

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
    min_price = 0.0

    for ticker in tickers:
        if ticker is not None:
            min_price = max(min_price, ticker.ask)

    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if min_price != 0.0:
        return MIN_VOLUME_COEFFICIENT[base_currency_id] / min_price

    return 0.0


def compute_min_cap_from_ticker(pair_id, ticker):
    min_price = 0.0

    if ticker is not None:
        min_price = max(min_price, ticker.ask)

    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if min_price != 0.0:
        return MIN_VOLUME_COEFFICIENT[base_currency_id] / min_price

    return 0.0
