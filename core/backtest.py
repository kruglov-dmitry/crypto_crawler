from constants import ARBITRAGE_CURRENCY

from enums.exchange import EXCHANGE
from enums.currency import CURRENCY

from data.Balance import Balance
from data.BalanceState import BalanceState
from data.MarketCap import MarketCap

from utils.time_utils import get_now_seconds_local

def dummy_balance_init(timest, default_volume, balance_adjust_threshold):
    balance = {}

    initial_balance = {}

    for currency_id in ARBITRAGE_CURRENCY:
        initial_balance[currency_id] = default_volume

    for exchange_id in EXCHANGE.values():
        balance[exchange_id] = Balance(exchange_id, timest, initial_balance)

    return BalanceState(balance, balance_adjust_threshold)


def dummy_order_state_init():
    order_state_by_exchange = {}

    open_orders = []
    closed_orders = []

    timest = get_now_seconds_local()

    for exchange_id in EXCHANGE.values():
        order_state_by_exchange[exchange_id] = None

    return order_state_by_exchange


def custom_balance_init(timest, balance_adjust_threshold):

    # CURRENCY.BITCOIN, CURRENCY.DASH, CURRENCY.BCC, CURRENCY.XRP, CURRENCY.LTC, CURRENCY.ETC, CURRENCY.ETH
    # EXCHANGE.POLONIEX_EXCHANGE, EXCHANGE.KRAKEN_EXCHANGE, EXCHANGE.BITTREX_EXCHANGE

    balance = {}

    poloniex_balance = {CURRENCY.BITCOIN: 10.0, CURRENCY.DASH: 15.0, CURRENCY.BCC: 13.0, CURRENCY.XRP: 30000.0,
                        CURRENCY.LTC: 100.0, CURRENCY.ETC: 600.0, CURRENCY.ETH: 20.0}

    balance[EXCHANGE.POLONIEX] = Balance(EXCHANGE.POLONIEX, timest, poloniex_balance)

    kraken_balance = {CURRENCY.BITCOIN: 10.0, CURRENCY.DASH: 15.0, CURRENCY.BCC: 13.0, CURRENCY.XRP: 30000.0,
                      CURRENCY.LTC: 100.0, CURRENCY.ETC: 600.0, CURRENCY.ETH: 20.0}

    balance[EXCHANGE.KRAKEN] = Balance(EXCHANGE.KRAKEN, timest, kraken_balance)

    bittrex_balance = {CURRENCY.BITCOIN: 10.0, CURRENCY.DASH: 15.0, CURRENCY.BCC: 13.0, CURRENCY.XRP: 30000.0,
                       CURRENCY.LTC: 100.0, CURRENCY.ETC: 600.0, CURRENCY.ETH: 20.0}

    balance[EXCHANGE.BITTREX] = Balance(EXCHANGE.BITTREX, timest, bittrex_balance)

    return BalanceState(balance, balance_adjust_threshold)


def common_cap_init():

    min_volume_cap = {CURRENCY.BITCOIN: 0.0, CURRENCY.DASH: 0.03,
                      CURRENCY.BCC: 0.008, CURRENCY.XRP: 30.0,
                      CURRENCY.LTC: 0.1, CURRENCY.ETC:  0.45, CURRENCY.ETH: 0.02,
                      CURRENCY.XEM: 0.0, CURRENCY.DGB: 0.0, CURRENCY.ARDR: 0.0,
                      CURRENCY.OMG: 0.0, CURRENCY.USDT: 0.0, CURRENCY.DCR: 0.0
                      }

    max_volume_cap = {CURRENCY.BITCOIN: 100500.0, CURRENCY.DASH: 100500.0,
                      CURRENCY.BCC: 100500.0, CURRENCY.XRP: 100500.0,
                      CURRENCY.LTC: 100500.0, CURRENCY.ETC: 100500.0, CURRENCY.ETH: 100500.0,
                      CURRENCY.XEM: 100500.0, CURRENCY.DGB: 100500.0, CURRENCY.ARDR: 100500.0,
                      CURRENCY.OMG: 100500.0, CURRENCY.USDT: 100500.0, CURRENCY.DCR: 100500.0}

    min_price_cap = {CURRENCY.BITCOIN: 0.0}

    max_price_cap = {CURRENCY.BITCOIN: 0.01}

    return MarketCap(min_volume_cap, max_volume_cap, min_price_cap, max_price_cap)
