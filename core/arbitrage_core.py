import sys
import json
import re

sys.setrecursionlimit(10000)

from dao.dao import buy_by_exchange, sell_by_exchange, get_updated_order_state
from dao.balance_utils import get_updated_balance

from dao.order_book_utils import get_order_book_by_pair
from dao.balance_utils import update_balance_by_exchange

from utils.key_utils import load_keys
from debug_utils import should_print_debug, print_to_console, LOG_ALL_ERRORS, LOG_ALL_MARKET_NETWORK_RELATED_CRAP
from utils.time_utils import get_now_seconds_utc
from utils.currency_utils import split_currency_pairs, get_pair_name_by_id, get_currency_pair_name_by_exchange_id
from utils.exchange_utils import get_exchange_name_by_id
from utils.file_utils import log_to_file
from utils.string_utils import float_to_str
from utils.key_utils import get_key_by_exchange

from core.base_analysis import get_change
from core.base_math import get_all_combination

from enums.exchange import EXCHANGE
from enums.deal_type import DEAL_TYPE
from enums.status import STATUS
from enums.notifications import NOTIFICATION

from data.Trade import Trade
from data.TradePair import TradePair

from binance.market_utils import add_buy_order_binance_url, add_sell_order_binance_url
from kraken.market_utils import add_buy_order_kraken_url, add_sell_order_kraken_url
from bittrex.market_utils import add_buy_order_bittrex_url, add_sell_order_bittrex_url
from poloniex.market_utils import add_buy_order_poloniex_url, add_sell_order_poloniex_url
from data_access.ConnectionPool import WorkUnit


from constants import ARBITRAGE_PAIRS, DEAL_MAX_TIMEOUT

from data_access.telegram_notifications import send_single_message

from core.backtest import common_cap_init, dummy_balance_init, dummy_order_state_init

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


def is_no_pending_order(currency_id, src_exchange_id, dst_exchange_id):
    # FIXME - have to load active deals per exchange >_<
    return True


def init_deal(trade_to_perform, debug_msg):
    res = STATUS.FAILURE, None
    try:
        if trade_to_perform.trade_type == DEAL_TYPE.SELL:
            res = sell_by_exchange(trade_to_perform)
        else:
            res = buy_by_exchange(trade_to_perform)
    except Exception, e:
        msg = "init_deal: FAILED ERROR WE ALL DIE with following exception: {excp} {dbg}".format(excp=str(e),
                                                                                                 dbg=debug_msg)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")

    # force update balance at exchanges
    update_balance_by_exchange(trade_to_perform.exchange_id)

    return res


def init_deals_with_logging(trade_pairs, difference, file_name):
    global overall_profit_so_far

    first_deal = trade_pairs.deal_1
    second_deal = trade_pairs.deal_2

    if second_deal.exchange_id == EXCHANGE.KRAKEN:
        # It is hilarious but if deal at kraken will not succeeded no need to bother with second exchange
        first_deal = trade_pairs.deal_2
        second_deal = trade_pairs.deal_1

    # market routine
    debug_msg = "Deals details: " + str(first_deal)
    result_1 = init_deal(first_deal, debug_msg)

    first_deal.execute_time = get_now_seconds_utc()

    if result_1[0] != STATUS.SUCCESS:
        msg = "Failing of adding FIRST deal! {deal}".format(deal=str(first_deal))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")
        return STATUS.FAILURE

    debug_msg = "Deals details: " + str(second_deal)
    result_2 = init_deal(second_deal, debug_msg)

    second_deal.execute_time = get_now_seconds_utc()

    if result_1[0] == STATUS.FAILURE or result_2[0] == STATUS.FAILURE:
        msg = "Failing of adding deals! {deal_pair}".format(deal_pair=str(trade_pairs))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, "error.log")
        return STATUS.FAILURE

    overall_profit_so_far += trade_pairs.current_profit

    msg = "Some deals sent to exchanges. Expected profit: {cur}. Overall: {tot} Difference in percents: " \
          "{diff} Deal details: {deal}".format(cur=float_to_str(trade_pairs.current_profit),
                                               tot=float_to_str(overall_profit_so_far),
                                               diff=difference, deal=str(trade_pairs))

    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(trade_pairs, file_name)

    send_single_message(msg, NOTIFICATION.DEAL)

    return STATUS.SUCCESS


def init_deals_with_logging_speedy_fake(trade_pairs, difference, file_name, processor):
    pass

def init_deals_with_logging_speedy(trade_pairs, difference, file_name, processor):
    parallel_deals = []

    for trade in [trade_pairs.deal_1, trade_pairs.deal_2]:

        method_for_url = get_method_for_create_url_trade_by_exchange_id(trade)
        # key, pair_name, price, amount
        key = get_key_by_exchange(trade.exchange_id)
        pair_name = get_currency_pair_name_by_exchange_id(trade.pair_id, trade.exchange_id)
        post_details = method_for_url(key, pair_name, trade.price, trade.volume)
        constructor = return_with_no_change

        wu = WorkUnit(post_details.final_url, constructor, trade)
        wu.add_post_details(post_details)

        parallel_deals.append(wu)

    res = processor.process_async_post(parallel_deals, DEAL_MAX_TIMEOUT)

    global overall_profit_so_far
    overall_profit_so_far += trade_pairs.current_profit

    msg = """
            We try to send following deals to exchange.
    <b>Expected profit:</b> <i>{cur}</i>. 
    <b>Overall:</b> <i>{tot}</i>
    <b>Difference in percents:</b> <i>{diff}</i>
    
            Deal details:
    {deal}
    """.format(
        cur=float_to_str(trade_pairs.current_profit),
        tot=float_to_str(overall_profit_so_far),
        diff=difference, deal=str(trade_pairs))

    log_to_file(msg, file_name)
    send_single_message(msg, NOTIFICATION.DEAL)

    # check for errors only
    for (return_value, trade) in res:
        # check for none and error_code may not be jsonable
        if return_value.status_code == 200:
            msg = """
            For trade {trade}
            Response is {resp} """.format(trade=trade, resp=return_value.json())
        else:
            response_json = "Not provided"
            try:
                response_json = return_value.json()
            except:
                pass
            msg = """
            For trade {trade}
            Response is <b>BAD CODE!</b> {resp} and exact json - {js}""".format(
                trade=trade,
                resp=str(return_value.status_code),
                js=response_json
            )

        print_to_console(msg, LOG_ALL_ERRORS)
        send_single_message(msg, NOTIFICATION.DEBUG)
        log_to_file(msg, file_name)

    # FIXME NOTE: and now good question - what to do with failed deals.


def get_method_for_create_url_trade_by_exchange_id(trade):
    return {
        DEAL_TYPE.BUY: {
            EXCHANGE.BINANCE: add_buy_order_binance_url,
            EXCHANGE.BITTREX: add_buy_order_bittrex_url,
            EXCHANGE.POLONIEX: add_buy_order_poloniex_url,
            EXCHANGE.KRAKEN: add_buy_order_kraken_url,
        },
        DEAL_TYPE.SELL: {
            EXCHANGE.BINANCE: add_sell_order_binance_url,
            EXCHANGE.BITTREX: add_sell_order_bittrex_url,
            EXCHANGE.POLONIEX: add_sell_order_poloniex_url,
            EXCHANGE.KRAKEN: add_sell_order_kraken_url,
        }
    }[trade.trade_type][trade.exchange_id]


def return_with_no_change(json_document, corresponding_trade):
    corresponding_trade.execute_time = get_now_seconds_utc()
    return json_document, corresponding_trade


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
        log_to_file(msg, "error.log")
        raise

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
        min_volume = second_order_book.ask[LAST].price * balance_state.get_available_volume_by_currency(
            base_currency_id, second_order_book.exchange_id)

    return min_volume


def adjust_minimum_volume_by_trading_cap(first_order_book, second_order_book, deal_cap, min_volume):
    if min_volume < deal_cap.get_min_volume_cap_by_dst(first_order_book.pair_id):
        min_volume = -1  # Yeap, no need to even bother

    return min_volume


def search_for_arbitrage(sell_order_book, buy_order_book, threshold,
                         action_to_perform,
                         balance_state, deal_cap,
                         type_of_deal, worker_pool):
    """
    FIXMR NOTE - add comments!
    :param sell_order_book:
    :param buy_order_book:
    :param threshold:
    :param action_to_perform:
    :param balance_state:
    :param deal_cap:
    :param type_of_deal:
    :return:
    """

    if len(sell_order_book.bid) == 0 or len(buy_order_book.ask) == 0:
        return STATUS.SUCCESS

    difference = get_change(sell_order_book.bid[FIRST].price, buy_order_book.ask[LAST].price, provide_abs=False)

    if should_print_debug():
        msg = """check_highest_bid_bigger_than_lowest_ask:
        For pair - {pair_name}
        Exchange1 - {exch1} BID = {bid}
        Exchange2 - {exch2} ASK = {ask}
        DIFF = {diff}""".format(
            pair_name=get_pair_name_by_id(sell_order_book.pair_id),
            exch1=get_exchange_name_by_id(sell_order_book.exchange_id),
            bid=float_to_str(sell_order_book.bid[FIRST].price),
            exch2=get_exchange_name_by_id(buy_order_book.exchange_id),
            ask=float_to_str(buy_order_book.ask[LAST].price),
            diff=difference)
        print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
        log_to_file(msg, "debug.log")

    if difference >= threshold:

        min_volume = determine_minimum_volume(sell_order_book, buy_order_book, balance_state)

        min_volume = adjust_minimum_volume_by_trading_cap(sell_order_book, buy_order_book, deal_cap, min_volume)

        if min_volume <= 0:
            msg = """analyse order book - DETERMINED volume of deal is not ENOUGH {pair_name}:
            first_exchange: {first_exchange} first exchange volume: <b>{vol1}</b>
            second_exchange: {second_exchange} second_exchange_volume: <b>{vol2}</b>""".format(
                pair_name=get_pair_name_by_id(sell_order_book.pair_id),
                first_exchange=get_exchange_name_by_id(sell_order_book.exchange_id),
                second_exchange=get_exchange_name_by_id(buy_order_book.exchange_id),
                vol1=float_to_str(sell_order_book.bid[FIRST].volume),
                vol2=float_to_str(buy_order_book.ask[LAST].volume))
            print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
            log_to_file(msg, "debug.log")
            send_single_message(msg, NOTIFICATION.DEBUG)

            return STATUS.FAILURE

        create_time = get_now_seconds_utc()
        trade_at_first_exchange = Trade(DEAL_TYPE.SELL, sell_order_book.exchange_id, sell_order_book.pair_id,
                                        sell_order_book.bid[FIRST].price, min_volume, sell_order_book.timest,
                                        create_time)

        trade_at_second_exchange = Trade(DEAL_TYPE.BUY, buy_order_book.exchange_id, buy_order_book.pair_id,
                                         buy_order_book.ask[LAST].price, min_volume, buy_order_book.timest,
                                         create_time)

        deal_status = action_to_perform(TradePair(trade_at_first_exchange, trade_at_second_exchange,
                                                  sell_order_book.timest, buy_order_book.timest, type_of_deal),
                                        difference,
                                        "history_trades.log",
                                        worker_pool)

        if deal_status == STATUS.FAILURE:
            # We are going to stop recursion here due to simple reason
            # we have 3 to 5 re-tries within placing orders
            # if for any reason they not succeeded - it mean we already spend more than one minute
            # and our orderbook is expired already so we should stop recursive calls
            return STATUS.FAILURE

        return STATUS.SUCCESS


def adjust_currency_balance(first_order_book, second_order_book, treshold_reverse, action_to_perform,
                            balance_state, deal_cap, type_of_deal, worker_pool):
    pair_id = first_order_book.pair_id
    src_currency_id, dst_currency_id = split_currency_pairs(pair_id)
    src_exchange_id = first_order_book.exchange_id
    dst_exchange_id = second_order_book.exchange_id

    if balance_state.is_there_disbalance(dst_currency_id, src_exchange_id, dst_exchange_id, treshold_reverse) and \
            is_no_pending_order(pair_id, src_exchange_id, dst_exchange_id):
        msg = "We have disbalance! Exchanges {exch1} {exch2} for {pair_id} with {thrs}".format(
            exch1=get_exchange_name_by_id(src_exchange_id),
            exch2=get_exchange_name_by_id(dst_exchange_id),
            pair_id=get_pair_name_by_id(dst_currency_id),
            thrs=treshold_reverse
        )

        print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
        log_to_file(msg, "history_trades.log")

        search_for_arbitrage(first_order_book, second_order_book, treshold_reverse,
                             action_to_perform, balance_state, deal_cap,
                             type_of_deal, worker_pool)
    else:
        msg = "No disbalance at Exchanges {exch1} {exch2} for {pair_id} with {thrs}".format(
            exch1=get_exchange_name_by_id(src_exchange_id),
            exch2=get_exchange_name_by_id(dst_exchange_id),
            pair_id=get_pair_name_by_id(dst_currency_id),
            thrs=treshold_reverse
        )
        print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
        log_to_file(msg, "debug.log")


def mega_analysis(order_book, threshold, balance_state, deal_cap, action_to_perform):
    """
    :param order_book: dict of lists with order book, where keys are exchange names within particular time window
            either request timeout or by timest window during playing within database
    :param threshold: minimum difference of ask vs bid in percent that should trigger deal
    :param balance_state
    :param deal_cap
    :param action_to_perform: method, that take details of ask bid at two exchange and trigger deals
    :return:
    """

    order_book_pairs = get_all_combination(order_book, 2)

    for every_pair in order_book_pairs:
        src_exchange_id, dst_exchange_id = every_pair
        first_order_book = order_book[src_exchange_id]
        second_order_book = order_book[dst_exchange_id]

        search_for_arbitrage(first_order_book[0],
                             second_order_book[0],
                             threshold,
                             action_to_perform,
                             balance_state,
                             deal_cap,
                             type_of_deal=DEAL_TYPE.ARBITRAGE)


def run_bot(deal_threshold):
    load_keys("./secret_keys")
    deal_cap = common_cap_init()
    cur_timest = get_now_seconds_utc()
    current_balance = dummy_balance_init(cur_timest, 0, 0)
    order_state = dummy_order_state_init()

    while True:

        current_balance = get_updated_balance(current_balance)
        order_state = get_updated_order_state(order_state)

        for pair_id in ARBITRAGE_PAIRS:
            order_book = get_order_book_by_pair(pair_id)
            mega_analysis(order_book, deal_threshold, current_balance, deal_cap, init_deals_with_logging)


if __name__ == "__main__":

    print "THIS SHOULD NOt BE EXECUtED DIRECTLY! "
    raise

    pg_conn = init_pg_connection()

    # FIXME - read from some config
    deal_threshold = 0.6
    treshold_reverse = 0.6
    balance_adjust_threshold = 5.0

    run_bot(deal_threshold)
