from constants import ARBITRAGE_CURRENCY

from enums.exchange import EXCHANGE
from enums.currency import CURRENCY

from data.Balance import Balance
from data.BalanceState import BalanceState
from data.MarketCap import MarketCap

from utils.time_utils import get_now_seconds_utc
from utils.file_utils import log_to_file

from dao.db import init_pg_connection, get_order_book_by_time, get_time_entries



def dummy_order_state_init():
    order_state_by_exchange = {}

    for exchange_id in EXCHANGE.values():
        order_state_by_exchange[exchange_id] = None

    return order_state_by_exchange


def custom_balance_init(timest):

    balance = {}

    poloniex_balance = {CURRENCY.BITCOIN: 10.0,
                        CURRENCY.DASH: 15.0,
                        CURRENCY.BCC: 13.0,
                        CURRENCY.XRP: 30000.0,
                        CURRENCY.LTC: 100.0,
                        CURRENCY.ETC: 600.0,
                        CURRENCY.ETH: 20.0}

    balance[EXCHANGE.POLONIEX] = Balance(EXCHANGE.POLONIEX, timest, poloniex_balance, poloniex_balance)

    kraken_balance = {CURRENCY.BITCOIN: 10.0,
                      CURRENCY.DASH: 15.0,
                      CURRENCY.BCC: 13.0,
                      CURRENCY.XRP: 30000.0,
                      CURRENCY.LTC: 100.0,
                      CURRENCY.ETC: 600.0,
                      CURRENCY.ETH: 20.0}

    balance[EXCHANGE.KRAKEN] = Balance(EXCHANGE.KRAKEN, timest, kraken_balance, kraken_balance)

    bittrex_balance = {CURRENCY.BITCOIN: 10.0,
                       CURRENCY.DASH: 15.0,
                       CURRENCY.BCC: 13.0,
                       CURRENCY.XRP: 30000.0,
                       CURRENCY.LTC: 100.0,
                       CURRENCY.ETC: 600.0,
                       CURRENCY.ETH: 20.0}

    balance[EXCHANGE.BITTREX] = Balance(EXCHANGE.BITTREX, timest, bittrex_balance, bittrex_balance)

    # Just a self check to guarantee that our cap is up to date with active list of arbitrage currencies
    print("\t \t <<< ! ERROR ! >>> \n"
          "If this is one of the LAST message in stack trace it mean that deal Cap and Arbitrage currencies not update!")
    assert (len(ARBITRAGE_CURRENCY) == len(poloniex_balance))

    return BalanceState(balance)


def common_cap_init(timest=get_now_seconds_utc()):

    min_volume_cap = {CURRENCY.BITCOIN: 0.0,
                      CURRENCY.DASH: 0.03,
                      CURRENCY.BCC: 0.008,
                      CURRENCY.XRP: 30.0,
                      CURRENCY.LTC: 0.1,
                      CURRENCY.ETC:  0.45,
                      CURRENCY.ETH: 0.02,
                      CURRENCY.XEM: 40.0,
                      CURRENCY.DGB: 800.0,
                      CURRENCY.ARDR: 25.0,
                      CURRENCY.OMG: 1.25,
                      CURRENCY.USDT: 12.0,
                      CURRENCY.DCR: 0.25,
                      CURRENCY.REP: 0.35
                      }

    max_volume_cap = {CURRENCY.BITCOIN: 100500.0,
                      CURRENCY.DASH: 100500.0,
                      CURRENCY.BCC: 100500.0,
                      CURRENCY.XRP: 100500.0,
                      CURRENCY.LTC: 100500.0,
                      CURRENCY.ETC: 100500.0,
                      CURRENCY.ETH: 100500.0,
                      CURRENCY.XEM: 100500.0,
                      CURRENCY.DGB: 100500.0,
                      CURRENCY.ARDR: 100500.0,
                      CURRENCY.OMG: 100500.0,
                      CURRENCY.USDT: 100500.0,
                      CURRENCY.DCR: 100500.0,
                      CURRENCY.REP: 100500.0}

    min_price_cap = {CURRENCY.BITCOIN: 0.0}

    max_price_cap = {CURRENCY.BITCOIN: 1.0}

    # Just a self check to guarantee that our cap is up to date with active list of arbitrage currencies
    print("\t \t <<< ! ERROR ! >>> \n"
          "If this is one of the LAST message in stack trace it mean that deal Cap and Arbitrage currencies not update!")
    # assert(len(ARBITRAGE_CURRENCY) == len(max_volume_cap))

    return MarketCap(min_volume_cap, max_volume_cap, min_price_cap, max_price_cap, timest)


def run_analysis_over_db(deal_threshold, analysis_method):
    print "<<< WARNING >>> Non UPDATED FOR AGES."

    # FIXME NOTE: accumulate profit

    pg_conn = init_pg_connection()
    time_entries = get_time_entries(pg_conn)
    time_entries_num = len(time_entries)

    print "Order_book num: ", time_entries_num

    cnt = 0
    MAX_ORDER_BOOK_COUNT = 10000
    current_balance = custom_balance_init(time_entries[0])
    deal_cap = common_cap_init()

    for exchange_id in current_balance.balance_per_exchange:
        print current_balance.balance_per_exchange[exchange_id]

    for every_time_entry in time_entries:
        order_book_grouped_by_time = get_order_book_by_time(pg_conn, every_time_entry)

        for order_book in order_book_grouped_by_time:
            analysis_method (order_book, deal_threshold, current_balance, log_to_file, deal_cap)

        cnt += 1
        msg = "Processed order_book #{cnt} out of {total} time entries\n current_balance={balance}".format(
            cnt=cnt, total=time_entries_num, balance=str(current_balance))

        print msg
        log_to_file(msg, "history_trades.txt")

        if cnt == MAX_ORDER_BOOK_COUNT:
            raise

    print "At the end of processing we have following balance:"
    print "NOTE: supposedly all buy and sell requests were fulfilled"
    for exchange_id in current_balance.balance_per_exchange:
        print current_balance.balance_per_exchange[exchange_id]
