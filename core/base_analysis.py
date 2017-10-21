from enums.currency_pair import CURRENCY_PAIR
from debug_utils import should_print_debug


def compare_price(bittrex_tickers, kraken_tickers, poloniex_tickers, threshold, predicate):
    """
    High level function that perform tickers analysis

    :param bittrex_tickers:
    :param kraken_tickers:
    :param poloniex_tickers:
    :param threshold: percentage, 0-100.0, float to trigger event
    :return: array of triplets pair_id, exchange_1.lowest_price, exchange_2.highest_bid
    """
    res = []

    for every_currency in CURRENCY_PAIR.values():
        bittrex_ticker = None
        if every_currency in bittrex_tickers:
            bittrex_ticker = bittrex_tickers[every_currency]

        kraken_ticker = None
        if every_currency in kraken_tickers:
            kraken_ticker = kraken_tickers[every_currency]

        poloniex_ticker = None
        if every_currency in poloniex_tickers:
            poloniex_ticker = poloniex_tickers[every_currency]

        current_result = check_all_combinations(bittrex_ticker, kraken_ticker, poloniex_ticker, threshold, predicate)
        if current_result:
            res += current_result

    return res


def check_all_combinations(bittrex_ticker, kraken_ticker, poloniex_ticker, threshold, predicate):
    """
    FIXME TODO: generate permutation among input value in more general fashion!
    """

    res_list = []

    if bittrex_ticker is not None and kraken_ticker is not None:
        res = predicate(bittrex_ticker, kraken_ticker, threshold)
        if res:
            res_list.append(res)
        res = predicate(kraken_ticker, bittrex_ticker, threshold)
        if res:
            res_list.append(res)

    if poloniex_ticker is not None and kraken_ticker is not None:
        res = predicate(kraken_ticker, poloniex_ticker, threshold)
        if res:
            res_list.append(res)
        res = predicate(poloniex_ticker, kraken_ticker, threshold)
        if res:
            res_list.append(res)

    if bittrex_ticker is not None and poloniex_ticker is not None:
        res = predicate(bittrex_ticker, poloniex_ticker, threshold)
        if res:
            res_list.append(res)
        res = predicate(poloniex_ticker, bittrex_ticker, threshold)
        if res:
            res_list.append(res)

    return res_list


def get_diff_lowest_ask_vs_highest_bid(first_one, second_one, threshold):
    difference = get_change(first_one.ask, second_one.bid)

    if should_print_debug():
        print "get_diff_lowest_ask_vs_highest_bid: ASK = {ask} BID = {bid} DIFF={diff}".format(
            ask=first_one.ask, bid=second_one.bid, diff=difference)

    if difference >= threshold:
        msg = "Lowest ask differ from highest bid more than {num} %".format(num=threshold)
        return msg, first_one.pair_id, first_one, second_one

    return ()


def check_highest_bid_bigger_than_lowest_ask(first_one, second_one, threshold):
    difference = get_change(first_one.bid, second_one.ask, provide_abs=False)

    if should_print_debug():
        print "check_highest_bid_bigger_than_lowest_ask"
        print "ASK: ", first_one.bid
        print "BID: ", second_one.ask
        print "DIFF: ", difference

    if difference >= threshold:
        msg = "highest bid bigger than Lowest ask for more than {num} %".format(num=threshold)
        return msg, first_one.pair_id, first_one, second_one

    return ()


def get_change(current, previous, provide_abs=True):
    """

    :param current:
    :param previous:
    :return: difference in percentage between current & previous
    """

    tot = 0.5 * (current + previous)
    diff = 0.0
    if provide_abs:
        diff = abs(current - previous)
    else:
        diff = current - previous

    percent = 100.0

    if tot != 0:
        percent = ((diff / tot) * 100)

    return percent
