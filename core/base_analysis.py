from collections import defaultdict
from decimal import Decimal

from enums.currency_pair import CURRENCY_PAIR
from utils.debug_utils import should_print_debug, print_to_console, LOG_ALL_MARKET_RELATED_CRAP
from utils.file_utils import log_to_file
from utils.string_utils import truncate_float
from core.base_math import get_all_permutation, get_all_permutation_list


def get_matches(objs, key):
    """
        Return dict of list curresponding to key
    """
    d = defaultdict(list)
    for obj in objs:
        if obj is not None:
            d[getattr(obj, key)].append(obj)
    return d


def compare_price(tickers, threshold, predicate):
    """
    High level function that perform tickers analysis

    :param tickers: dict of dict where data are structured by exchange_id -> pair_id
    :param threshold: percentage, 0-100.0, float to trigger event
    :return: array of triplets pair_id, exchange_1.lowest_price, exchange_2.highest_bid
    """
    res = []

    sorted_tickers = get_matches(tickers, "pair_id")

    for pair_id in CURRENCY_PAIR.values():
        if pair_id in sorted_tickers:
            tickers_to_check = sorted_tickers[pair_id]

            if len(tickers_to_check) < 2:
                for b in tickers_to_check:
                    log_to_file("Ticker: not found ticker from other markets: " + str(b),
                                "ticker.log")
            else:
                current_result = check_all_combinations_list(tickers_to_check, threshold, predicate)
                if current_result:
                    res += current_result

    return res


def check_all_combinations(tickers_to_check, threshold, predicate):

    res_list = []

    pair_of_tickers = get_all_permutation(tickers_to_check, 2)

    for first_ticker, second_ticker in pair_of_tickers:
        res = predicate(first_ticker, second_ticker, threshold)
        if res:
            res_list.append(res)

    return res_list


def check_all_combinations_list(tickers_to_check, threshold, predicate):

    res_list = []

    pair_of_tickers = get_all_permutation_list(tickers_to_check, 2)

    for first_ticker, second_ticker in pair_of_tickers:
        res = predicate(first_ticker, second_ticker, threshold)
        if res:
            res_list.append(res)

    return res_list


def get_diff_lowest_ask_vs_highest_bid(first_one, second_one, threshold):
    difference = get_change(first_one.ask, second_one.bid)

    if should_print_debug():
        msg = "get_diff_lowest_ask_vs_highest_bid: ASK = {ask} BID = {bid} DIFF={diff}".format(
            ask=first_one.ask, bid=second_one.bid, diff=difference)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)

    if difference >= threshold:
        msg = "Lowest ask differ from highest bid more than {num} %".format(num=threshold)
        return msg, first_one.pair_id, first_one, second_one

    return ()


def check_highest_bid_bigger_than_lowest_ask(first_one, second_one, threshold):

    if not first_one.bid or not second_one.ask:
        return

    difference = get_change(first_one.bid, second_one.ask, provide_abs=False)

    if should_print_debug():
        msg = """check_highest_bid_bigger_than_lowest_ask called for
        threshold = {threshold}
        BID: {bid:.7f}
        AKS: {ask:.7f}
        DIFF: {diff:.7f}
        """.format(threshold=threshold, bid=first_one.bid, ask=second_one.ask, diff=difference)
        print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)

    if difference >= threshold:
        factual_threshold = threshold
        severity_flag = ""
        if 5.0 < difference < 10.0:
            severity_flag = "<b> ! ACT NOW ! </b>"
            factual_threshold = 5.0
        elif difference > 10.0:
            severity_flag = "<b>!!! ACT IMMEDIATELY !!!</b>"
            factual_threshold = 10.0
        msg = """{severity_flag}
        highest bid bigger than Lowest ask for more than {num} - <b>{diff:.7f}</b>""".format(
            severity_flag=severity_flag, num=factual_threshold, diff=difference)
        return msg, first_one.pair_id, first_one, second_one

    return ()


def get_change(current, previous, provide_abs=True):
    """

    :param provide_abs:
    :param current:
    :param previous:
    :return: difference in percentage between current & previous
    """

    tot = Decimal(0.5) * Decimal(current + previous)

    if provide_abs:
        diff = Decimal(abs(current - previous))
    else:
        diff = Decimal(current - previous)

    # FIXME NOTE: What if price would be different in multiple times?
    percent = 0.001

    if tot != 0:
        z = diff / tot
        if z > 0.001:
            percent = truncate_float((z * 100), 2)

    return percent
