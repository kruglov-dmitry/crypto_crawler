import sys
sys.setrecursionlimit(10000)

from dao.dao import buy_by_exchange, sell_by_exchange, get_updated_balance, get_order_book_by_pair, \
    get_updated_order_state
from dao.db import init_pg_connection, get_order_book_by_time, get_time_entries

from utils.key_utils import load_keys
from debug_utils import should_print_debug
from utils.time_utils import sleep_for, get_now_seconds_local
from utils.currency_utils import split_currency_pairs, get_pair_name_by_id
from utils.exchange_utils import get_exchange_name_by_id
from utils.file_utils import log_to_file

from core.base_analysis import get_change
from core.base_math import get_all_combination

from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE
from enums.currency import CURRENCY
from enums.status import STATUS

from data.Trade import Trade
from data.TradePair import TradePair

from constants import ARBITRAGE_PAIRS

from data_access.telegram_notifications import send_single_message

from core.backtest import common_cap_init, dummy_balance_init, dummy_order_state_init, custom_balance_init

from multiprocessing import Pool


# FIXME NOTE:
# This is indexes for comparison bid\ask within order books
# yeap, global constants is very bad
FIRST = 0
LAST = 0

# time to poll - 2 MINUTES
POLL_PERIOD_SECONDS = 7

# FIXME NOTES:
# 1. load current deals set?
# 2. integrate to bot commands to show active deal and be able to cancel them by command in chat?
# 3. take into account that we may need to change frequency of polling based on prospectivness of currency pair

# FIXME NOTE - global variables are VERY bad
overall_profit_so_far = 0.0


# pool_size = 1 # len(ARBITRAGE_CURRENCY) * len(EXCHANGE.values()) * 2
# process_pool = Pool(pool_size)


def is_no_pending_order(currency_id, src_exchange_id, dst_exchange_id):
    # FIXME - have to load active deals per exchange >_<
    return True


def init_deal(trade_to_perform, order_state, debug_msg):
    res = STATUS.FAILURE, None
    try:
        if trade_to_perform.trade_type == DEAL_TYPE.SELL:
            res = sell_by_exchange(trade_to_perform, order_state)
        else:
            res = buy_by_exchange(trade_to_perform, order_state)
    except Exception, e:
        msg = "init_deal: FAILED ERROR WE ALL DIE with following exception: {excp} {dbg}".format(excp=str(e), dbg=debug_msg)
        print msg
        log_to_file(msg, "debug.txt")

    return res


def init_deals_with_logging(trade_pairs, order_state,  file_name):

    global overall_profit_so_far

    first_deal = trade_pairs.deal_1
    second_deal = trade_pairs.deal_2

    if second_deal.exchange_id == EXCHANGE.KRAKEN:
        # It is hilarious but if deal at kraken will not succeeded no need to bother with second exchange
        first_deal = trade_pairs.deal_2
        second_deal = trade_pairs.deal_1

    # market routine
    debug_msg = "Deals details: " + str(first_deal)
    result_1 = init_deal(first_deal, order_state, debug_msg)

    first_deal.execute_time = get_now_seconds_local()

    if result_1[0] != STATUS.SUCCESS:
        msg = "Failing of adding FIRST deal! {deal}".format(deal=str(first_deal))
        print msg
        log_to_file(msg, file_name)
        return STATUS.FAILURE

    debug_msg = "Deals details: " + str(second_deal)
    result_2 = init_deal(second_deal, order_state, debug_msg)

    second_deal.execute_time = get_now_seconds_local()

    if result_1[0] == STATUS.FAILURE or result_2[0] == STATUS.FAILURE:
        msg = "Failing of adding deals! {deal_pair}".format(deal_pair=str(trade_pairs))
        print msg
        log_to_file(msg, file_name)
        return STATUS.FAILURE

    overall_profit_so_far += trade_pairs.current_profit

    msg = "Some deals sent to exchanges. Expected profit: {cur}. Overall: {tot} Deal details: {deal}".format(
        cur=trade_pairs.current_profit, tot=overall_profit_so_far, deal=str(trade_pairs))

    print msg
    # Logging TODO save to postgres
    log_to_file(trade_pairs, file_name)

    send_single_message(msg)

    return STATUS.SUCCESS


def determine_minimum_volume(first_order_book, second_order_book, balance_state):
    """
        we are going to SELL something at first exchange
        we are going to BUY something at second exchange
        This method determine maximum available volume of DST_CURRENCY on BOTH exchanges

    :param first_order_book:
    :param second_order_book:
    :param balance_state:
    :return:
    """

    min_volume = min(first_order_book.bid[FIRST].volume, second_order_book.ask[LAST].volume)
    if min_volume <= 0:
        msg = "analyse_order_book - something severely wrong - NEGATIVE min price: {pr}".format(pr=min_volume)
        print msg
        log_to_file(msg, "debug.txt")
        raise

    bitcoin_id, dst_currency_id = split_currency_pairs(first_order_book.pair_id)

    if not balance_state.do_we_have_enough(dst_currency_id,
                                           first_order_book.exchange_id,
                                           min_volume):
        min_volume = balance_state.get_available_volume_by_currency(dst_currency_id, first_order_book.exchange_id)

    if not balance_state.do_we_have_enough_by_pair(first_order_book.pair_id,
                                                   second_order_book.exchange_id,
                                                   min_volume,
                                                   second_order_book.ask[LAST].price):
        min_volume = second_order_book.ask[LAST].price * balance_state.get_available_volume_by_currency(bitcoin_id, second_order_book.exchange_id)

    return min_volume


def determine_minimum_volume_by_price(first_order_book, second_order_book, deal_cap, min_volume):
    if min_volume <= 0:
        return min_volume

    min_volume = min(min_volume, deal_cap.get_max_volume_cap_by_dst(first_order_book.pair_id))

    """if deal_cap.is_deal_size_acceptable(pair_id=first_order_book.pair_id, dst_currency_volume=min_volume,
    sell_price=first_order_book.bid[FIRST].price, buy_price=second_order_book.ask[LAST].price):"""

    # Maximum cost of price: neither sell or buy for more than X Bitcoin
    if min_volume * first_order_book.bid[FIRST].price > deal_cap.max_price_cap[CURRENCY.BITCOIN]:
        min_volume = deal_cap.max_price_cap[CURRENCY.BITCOIN] / float(first_order_book.bid[FIRST].price)
    if min_volume * second_order_book.ask[LAST].price > deal_cap.max_price_cap[CURRENCY.BITCOIN]:
        min_volume = deal_cap.max_price_cap[CURRENCY.BITCOIN] / float(second_order_book.ask[LAST].price)

    if min_volume < deal_cap.get_min_volume_cap_by_dst(first_order_book.pair_id):
        min_volume = -1 # Yeap, no need to even bother

    return min_volume


def analyse_order_book(first_order_book,
                       second_order_book,
                       threshold,
                       action_to_perform,
                       balance_state,
                       deal_cap,
                       order_state,
                       stop_recursion,
                       type_of_deal):
    """
    FIXMR NOTE - add comments!
    :param first_order_book:
    :param second_order_book:
    :param threshold:
    :param action_to_perform:
    :param balance_state:
    :param deal_cap:
    :param stop_recursion:
    :param type_of_deal:
    :return:
    """

    if len(first_order_book.bid) == 0 or len(second_order_book.ask) == 0:
        return STATUS.SUCCESS

    difference = get_change(first_order_book.bid[FIRST].price, second_order_book.ask[LAST].price, provide_abs=False)

    if should_print_debug():
        msg = "check_highest_bid_bigger_than_lowest_ask: BID = {bid} ASK = {ask}  DIFF = {diff}".format(
            bid=first_order_book.bid[FIRST].price, ask=second_order_book.ask[LAST].price, diff=difference)
        print msg
        log_to_file(msg, "debug.txt")

    if difference >= threshold:

        min_volume = determine_minimum_volume(first_order_book, second_order_book, balance_state)

        min_volume = determine_minimum_volume_by_price(first_order_book, second_order_book, deal_cap, min_volume)

        if min_volume <= 0:
            msg = "analyse_order_book - balance is ZERO!!! {pair_name} first_exchange: {first_exchange} " \
                  "second_exchange: {second_exchange}".format(
                pair_name=get_pair_name_by_id(first_order_book.pair_id),
                first_exchange=get_exchange_name_by_id(first_order_book.exchange_id),
                second_exchange=get_exchange_name_by_id(second_order_book.exchange_id))
            print msg
            log_to_file(msg, "debug.txt")
            send_single_message(msg)

            return

        create_time = get_now_seconds_local()
        trade_at_first_exchange = Trade(DEAL_TYPE.SELL, first_order_book.exchange_id, first_order_book.pair_id,
                                        first_order_book.bid[FIRST].price, min_volume, first_order_book.timest, create_time)

        trade_at_second_exchange = Trade(DEAL_TYPE.BUY, second_order_book.exchange_id, second_order_book.pair_id,
                                         second_order_book.ask[LAST].price, min_volume, second_order_book.timest, create_time)

        deal_status = action_to_perform(TradePair(trade_at_first_exchange, trade_at_second_exchange,
                                                  first_order_book.timest, second_order_book.timest, type_of_deal),
                                        order_state,
                                        "history_trades.txt")

        if deal_status == STATUS.FAILURE:
            # We are going to stop recursion here due to simple reason
            # we have 3 to 5 re-tries within placing orders
            # if for any reason they not succeeded - it mean we already spend more than one minute
            # and our orderbook is expired already so we should stop recursive calls
            return STATUS.FAILURE

        # FIXME NOTE - should be performed ONLY after deal confirmation
        balance_state.subtract_balance_by_pair(first_order_book, min_volume, first_order_book.bid[FIRST].price)
        balance_state.add_balance_by_pair(second_order_book, min_volume, second_order_book.ask[LAST].price)

        if len(first_order_book.bid) == 0 or len(second_order_book.ask) == 0:
            return STATUS.SUCCESS

        # adjust volumes
        if first_order_book.bid[FIRST].volume > min_volume:
            first_order_book.bid[FIRST].volume = first_order_book.bid[FIRST].volume - min_volume
            second_order_book.ask = second_order_book.ask[1:]
        elif second_order_book.ask[LAST].volume > min_volume:
            second_order_book.ask[LAST].volume = second_order_book.ask[LAST].volume - min_volume
            first_order_book.bid = first_order_book.bid[1:]

        if not stop_recursion:
            # continue processing remaining order book
            return analyse_order_book(first_order_book,
                                      second_order_book,
                                      threshold,
                                      action_to_perform,
                                      balance_state,
                                      deal_cap,
                                      order_state,
                                      stop_recursion,
                                      type_of_deal)


def adjust_currency_balance(first_order_book, second_order_book, treshold_reverse, action_to_perform,
                            balance_state, deal_cap, order_state):

    pair_id = first_order_book.pair_id
    src_currency_id, dst_currency_id = split_currency_pairs(pair_id)
    src_exchange_id = first_order_book.exchange_id
    dst_exchange_id = second_order_book.exchange_id

    order_book_expired = STATUS.SUCCESS
    # disbalance_state, treshold_reverse
    if balance_state.is_there_disbalance(dst_currency_id, src_exchange_id, dst_exchange_id) and \
            is_no_pending_order(pair_id, src_exchange_id, dst_exchange_id):

        order_book_expired = analyse_order_book(first_order_book,
                                                second_order_book,
                                                treshold_reverse,
                                                action_to_perform,
                                                balance_state,
                                                deal_cap,
                                                order_state,
                                                stop_recursion=True,
                                                type_of_deal=DEAL_TYPE.REVERSE)

    # FIXME NOTE - here we treat order book as unchanged, but it may already be affected by previous deals
    # previous call change bids of first order book & asks of second order book
    # but here we use oposite - i.e. should be fine

    # disbalance_state, treshold_reverse
    if order_book_expired == STATUS.SUCCESS and balance_state.is_there_disbalance(dst_currency_id, dst_exchange_id,src_exchange_id) \
            and is_no_pending_order(pair_id, dst_exchange_id, src_exchange_id):
        analyse_order_book(second_order_book,
                           first_order_book,
                           treshold_reverse,
                           action_to_perform,
                           balance_state,
                           deal_cap,
                           order_state,
                           stop_recursion=True,
                           type_of_deal=DEAL_TYPE.REVERSE)


def search_for_arbitrage(first_order_book,
                         second_order_book,
                         threshold,
                         action_to_perform,
                         balance_state,
                         deal_cap,
                         order_state):
    # FIXME NOTE - recursion will change them so we need to re-init it to apply vise-wersa processing

    order_book_expired = analyse_order_book(first_order_book,
                                            second_order_book,
                                            threshold,
                                            action_to_perform,
                                            balance_state,
                                            deal_cap,
                                            order_state,
                                            stop_recursion=False,
                                            type_of_deal=DEAL_TYPE.ARBITRAGE)

    # FIXME NOTE - here we treat order book as unchanged, but it may already be affected by previous deals
    # previous call change bids of first order book & asks of second order book
    # but here we use oposite - i.e. should be fine

    if order_book_expired == STATUS.SUCCESS:
        analyse_order_book(second_order_book,
                           first_order_book,
                           threshold,
                           action_to_perform,
                           balance_state,
                           deal_cap,
                           order_state,
                           stop_recursion=False,
                           type_of_deal=DEAL_TYPE.ARBITRAGE)


def mega_analysis(order_book, threshold, balance_state, order_state,  deal_cap, treshold_reverse, action_to_perform):
    """
    :param order_book: dict of lists with order book, where keys are exchange names within particular time window
            either request timeout or by timest window during playing within database
    :param threshold: minimum difference of ask vs bid in percent that should trigger deal
    :param balance_state
    :param deal_cap
    :param treshold_reverse
    :param action_to_perform: method, that take details of ask bid at two exchange and trigger deals
    :return:
    """

    order_book_pairs = get_all_combination(order_book, 2)

    for every_pair in order_book_pairs:
        src_exchange_id, dst_exchange_id = every_pair
        first_order_book = order_book[src_exchange_id]
        second_order_book = order_book[dst_exchange_id]

        search_for_arbitrage(first_order_book[0], second_order_book[0], threshold, action_to_perform, balance_state, deal_cap, order_state)
        adjust_currency_balance(second_order_book[0], first_order_book[0], treshold_reverse, action_to_perform, balance_state, deal_cap, order_state)

    # # split on currencies
    # for pair_id in CURRENCY_PAIR.values():

    #     # we interested ONLY in arbitrage related coins
    #     src_coin, dst_coin = split_currency_pairs(pair_id)
    #     if src_coin not in ARBITRAGE_CURRENCY or \
    #             dst_coin not in ARBITRAGE_CURRENCY:
    #         continue

    #     order_book_by_exchange_by_currency = defaultdict(list)

    #     for exchange_id in EXCHANGE.values():
    #         if exchange_id in order_book:
    #             exchange_order_book = [x for x in order_book[exchange_id] if x.pair_id == pair_id]

    #             # sort bids ascending and asks descending by price
    #             for x in exchange_order_book:
    #                 x.sort_by_price()

    #             order_book_by_exchange_by_currency[exchange_id] = exchange_order_book
    #         else:
    #             print "{0} exchange not present within order_book!".format(exchange_id)

    #     order_book_pairs = get_all_combination(order_book_by_exchange_by_currency, 2)

    #     for every_pair in order_book_pairs:
    #         src_exchange_id, dst_exchange_id = every_pair
    #         first_order_book = order_book_by_exchange_by_currency[src_exchange_id]
    #         second_order_book = order_book_by_exchange_by_currency[dst_exchange_id]

    #         if len(first_order_book) != 1 or len(second_order_book) != 1:
    #             print "Mega_analysis: Something severely wrong! First order book size - {size1} " \
    #                   "Second order book size - {size2} For currency - {currency_name} for Exchanges " \
    #                   "{exch1} and {exch2}".format(size1=len(first_order_book), size2=len(second_order_book),
    #                                                currency_name=get_pair_name_by_id(pair_id),
    #                                                exch1=get_exchange_name_by_id(src_exchange_id),
    #                                                exch2=get_exchange_name_by_id(dst_exchange_id))
    #             continue
    #         search_for_arbitrage(first_order_book[0], second_order_book[0], threshold, action_to_perform, balance_state, deal_cap)
    #         adjust_currency_balance(first_order_book[0], second_order_book[0], treshold_reverse, action_to_perform, balance_state, deal_cap)

    #         # Orkay, spawn a new process to have fun within
    #         # it will create deep copy of order book
    #         # process_pool.apply_async(search_for_arbitrage, args=(first_order_book[0], second_order_book[0], threshold, action_to_perform, balance_state, deal_cap))
    #         # process_pool.apply_async(adjust_currency_balance, args=(first_order_book[0], second_order_book[0], treshold_reverse, action_to_perform, balance_state, deal_cap))

    # # process_pool.close()
    # # process_pool.join()


def run_analysis_over_db(deal_threshold, balance_adjust_threshold, treshold_reverse):
    # FIXME NOTE: accumulate profit

    pg_conn = init_pg_connection()
    time_entries = get_time_entries(pg_conn)
    time_entries_num = len(time_entries)

    print "Order_book num: ", time_entries_num

    cnt = 0
    MAX_ORDER_BOOK_COUNT = 10000
    current_balance = custom_balance_init(time_entries[0], balance_adjust_threshold)
    deal_cap = common_cap_init()

    order_state = dummy_order_state_init()

    for exch_id in current_balance.balance_per_exchange:
        print current_balance.balance_per_exchange[exch_id]

    for every_time_entry in time_entries:
        order_book_grouped_by_time = get_order_book_by_time(pg_conn, every_time_entry)

        for x in order_book_grouped_by_time:
            mega_analysis(order_book_grouped_by_time,
                          deal_threshold,
                          current_balance,
                          order_state,
                          treshold_reverse,
                          log_to_file,
                          deal_cap)

        cnt += 1
        some_msg = "Processed order_book #{cnt} out of {total} time entries\n current_balance={balance}".format(
            cnt=cnt, total=time_entries_num, balance=str(current_balance))

        print some_msg

        log_to_file(some_msg, "history_trades.txt")

        if cnt == MAX_ORDER_BOOK_COUNT:
            raise

    print "At the end of processing we have following balance:"
    print "NOTE: supposedly all buy \ sell request were fullfilled"
    for exch_id in current_balance.balance_per_exchange:
        print current_balance.balance_per_exchange[exch_id]


def run_bot(deal_threshold, balance_adjust_threshold, treshold_reverse):
    load_keys("./secret_keys")
    deal_cap = common_cap_init()
    cur_timest = get_now_seconds_local()
    current_balance = dummy_balance_init(cur_timest, 0, 0, balance_adjust_threshold)
    order_state = dummy_order_state_init()

    while True:

        current_balance = get_updated_balance(balance_adjust_threshold, current_balance)
        order_state = get_updated_order_state(order_state)

        for pair_id in ARBITRAGE_PAIRS:
            order_book = get_order_book_by_pair(pair_id)

            # TODO: move this to single thread
            # process_pool.apply_async(
            mega_analysis(order_book, deal_threshold, current_balance, order_state, deal_cap, treshold_reverse,
                          init_deals_with_logging)

        # print "Before sleep..."
        # sleep_for(POLL_PERIOD_SECONDS)


if __name__ == "__main__":
    pg_conn = init_pg_connection()

    # FIXME - read from some config
    deal_threshold = 1.5
    treshold_reverse = 0.6
    balance_adjust_threshold = 5.0

    # run_analysis_over_db(deal_threshold, balance_adjust_threshold, treshold_reverse)
    run_bot(deal_threshold, balance_adjust_threshold, treshold_reverse)
