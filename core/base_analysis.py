from enums.currency_pair import CURRENCY_PAIR
from daemon import should_print_debug


def compare_price(bittrex_tickers, kraken_tickers, poloniex_tickers, threshold):
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

        current_result = check_all_combinations(bittrex_ticker, kraken_ticker, poloniex_ticker, threshold)
        if current_result:
            res += current_result

    return res


def check_all_combinations(bittrex_ticker, kraken_ticker, poloniex_ticker, threshold):
    """
    FIXME TODO: generate permutation among input value in more general fashion!
    """

    res_list = []

    res = compare_ticket_pair(bittrex_ticker, kraken_ticker, threshold)
    if res:
        res_list.append(res)
    res = compare_ticket_pair(kraken_ticker, bittrex_ticker, threshold)
    if res:
        res_list.append(res)

    res = compare_ticket_pair(kraken_ticker, poloniex_ticker, threshold)
    if res:
        res_list.append(res)
    res = compare_ticket_pair(poloniex_ticker, kraken_ticker, threshold)
    if res:
        res_list.append(res)
    res = compare_ticket_pair(bittrex_ticker, poloniex_ticker, threshold)
    if res:
        res_list.append(res)
    res = compare_ticket_pair(poloniex_ticker, bittrex_ticker, threshold)
    if res:
        res_list.append(res)

    return res_list


def compare_ticket_pair(first_one, second_one, threshold):
    difference = get_change(first_one.ask, second_one.bid)

    if should_print_debug():
        print "ASK: ", first_one.ask
        print "BID: ", second_one.bid
        print "DIFF: ", difference

    if difference >= threshold:
        return first_one.pair_id, first_one, second_one

    return ()


def get_change(current, previous):
    """

    :param current:
    :param previous:
    :return: difference in percentage between current & previous
    """

    tot = 0.5 * (current + previous)
    diff = abs(current - previous)

    percent = ((diff / tot) * 100)

    return percent
