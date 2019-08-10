from utils.debug_utils import print_to_console, get_logging_level, LOG_ALL_TRACE, LOG_ALL_MARKET_NETWORK_RELATED_CRAP, \
    DEBUG_LOG_FILE_NAME

from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id, get_currency_name_by_id
from utils.file_utils import log_to_file
from utils.string_utils import float_to_str

from data_access.message_queue import DEBUG_INFO_MSG

from constants import FIRST, LAST


def log_currency_disbalance_present(src_exchange_id, dst_exchange_id, pair_id, currency_id,
                                    balance_threshold, new_max_cap_volume, treshold):

    msg = """We have disbalance! Exchanges {exch1} {exch2} for {pair_id} with {balance_threshold}. 
    Set max cap for {currency} to {vol} and try to find price diff more than {thrs}""".format(
        exch1=get_exchange_name_by_id(src_exchange_id),
        exch2=get_exchange_name_by_id(dst_exchange_id),
        pair_id=get_pair_name_by_id(pair_id),
        balance_threshold=balance_threshold,
        currency=get_currency_name_by_id(currency_id),
        vol=new_max_cap_volume,
        thrs=treshold
    )

    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(msg, "history_trades.log")
    log_to_file(msg, "cap_price_adjustment.log")


def log_currency_disbalance_heart_beat(src_exchange_id, dst_exchange_id, currency_id, treshold_reverse):
    msg = "No disbalance at Exchanges {exch1} {exch2} for {pair_id} with {thrs}".format(
        exch1=get_exchange_name_by_id(src_exchange_id),
        exch2=get_exchange_name_by_id(dst_exchange_id),
        pair_id=get_currency_name_by_id(currency_id),
        thrs=treshold_reverse
    )
    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(msg, DEBUG_LOG_FILE_NAME)


def log_arbitrage_heart_beat(sell_order_book, buy_order_book, difference):
    msg = """check_highest_bid_bigger_than_lowest_ask:
    \tFor pair - {pair_name}
    \tExchange1 - {exch1} BID = {bid}
    \tExchange2 - {exch2} ASK = {ask}
    \tDIFF = {diff}""".format(pair_name=get_pair_name_by_id(sell_order_book.pair_id),
                              exch1=get_exchange_name_by_id(sell_order_book.exchange_id),
                              bid=float_to_str(sell_order_book.bid[FIRST].price),
                              exch2=get_exchange_name_by_id(buy_order_book.exchange_id),
                              ask=float_to_str(buy_order_book.ask[LAST].price),
                              diff=difference)
    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(msg, DEBUG_LOG_FILE_NAME)


def log_arbitrage_determined_volume_not_enough(sell_order_book, buy_order_book, msg_queue):
    msg = """analyse order book - DETERMINED volume of deal is not ENOUGH {pair_name}:
    first_exchange: {first_exchange} first exchange volume: <b>{vol1}</b>
    second_exchange: {second_exchange} second_exchange_volume: <b>{vol2}</b>""".format(
        pair_name=get_pair_name_by_id(sell_order_book.pair_id),
        first_exchange=get_exchange_name_by_id(sell_order_book.exchange_id),
        second_exchange=get_exchange_name_by_id(buy_order_book.exchange_id),
        vol1=float_to_str(sell_order_book.bid[FIRST].volume),
        vol2=float_to_str(buy_order_book.ask[LAST].volume))
    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(msg, DEBUG_LOG_FILE_NAME)
    if get_logging_level() >= LOG_ALL_TRACE:
        msg_queue.add_message(DEBUG_INFO_MSG, msg)


def log_arbitrage_determined_price_not_enough(sell_price, sell_price_order_book, buy_price, buy_price_order_book,
                                              difference, final_difference, pair_id, msg_queue):
    msg = """analyse order book - adjusted prices below 0.2 hardcoded threshold:
    \tfinal_sell: {sell_price} initial_sell: {i_sell}
    \tfinal_buy: {final_buy} initial_buy: {i_buy}
    \tfinal_diff: {final_diff} original_diff: {diff} 
    \tfor pair_id = {p_name}""".format(sell_price=float_to_str(sell_price),
                                       i_sell=float_to_str(sell_price_order_book),
                                       final_buy=float_to_str(buy_price),
                                       i_buy=float_to_str(buy_price_order_book),
                                       final_diff=final_difference,
                                       p_name=get_pair_name_by_id(pair_id),
                                       diff=difference)
    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(msg, DEBUG_LOG_FILE_NAME)
    msg_queue.add_message(DEBUG_INFO_MSG, msg)
