import copy

from enums.status import STATUS
from enums.exchange import EXCHANGE

from data.BalanceState import BalanceState

from bittrex.balance_utils import get_balance_bittrex, get_balance_bittrex_post_details, \
    get_balance_bittrex_result_processor
from kraken.balance_utils import get_balance_kraken, get_balance_kraken_post_details, \
    get_balance_kraken_result_processor
from poloniex.balance_utils import get_balance_poloniex, get_balance_poloniex_post_details, \
    get_balance_poloniex_result_processor
from binance.balance_utils import get_balance_binance, get_balance_binance_post_details, \
    get_balance_binance_result_processor

from data_access.memory_cache import get_cache

from debug_utils import print_to_console, LOG_ALL_ERRORS, DEBUG_LOG_FILE_NAME
from utils.key_utils import get_key_by_exchange
from utils.file_utils import log_to_file
from utils.exchange_utils import get_exchange_name_by_id


def get_balance_by_exchange(exchange_id):
    res = STATUS.FAILURE, None

    key = get_key_by_exchange(exchange_id)

    if exchange_id == EXCHANGE.BITTREX:
        res = get_balance_bittrex(key)
    elif exchange_id == EXCHANGE.KRAKEN:
        res = get_balance_kraken(key)
    elif exchange_id == EXCHANGE.POLONIEX:
        res = get_balance_poloniex(key)
    elif exchange_id == EXCHANGE.BINANCE:
        res = get_balance_binance(key)
    else:
        msg = "get_balance_by_exchange - Unknown exchange! {idx}".format(idx=exchange_id)
        print_to_console(msg, LOG_ALL_ERRORS)

    a, b = res
    log_to_file(b, "balance.log")

    return res


def get_updated_balance(prev_balance):
    balance = {}

    for exchange_id in EXCHANGE.values():
        if exchange_id == EXCHANGE.KRAKEN or exchange_id == EXCHANGE.BINANCE:
            continue
        balance[exchange_id] = copy.deepcopy(prev_balance.balance_per_exchange[exchange_id])

        status_code, new_balance_value = get_balance_by_exchange(exchange_id)

        if status_code == STATUS.SUCCESS:
            balance[exchange_id] = new_balance_value
            log_to_file(new_balance_value, DEBUG_LOG_FILE_NAME)

    return BalanceState(balance)


def get_updated_balance_arbitrage(cfg, balance_state, local_cache):
    """
    Method is frequently called from numerous thread so in order to decrease load and number of request to exchanges,
    to avoid banning, we use cahed version of balance from memory cache.

    :param cfg: type: ArbitrageConfig
    :param balance_state:
    :param local_cache:
    :return: updated balance_state for request exchanges id
    """
    for exchange_id in [cfg.sell_exchange_id, cfg.buy_exchange_id]:
        balance = local_cache.get_balance(exchange_id)
        if balance is not None:
            balance_state.balance_per_exchange[exchange_id] = balance

    return balance_state


def get_balance_post_details_generator(exchange_id):
    return {
        EXCHANGE.BITTREX: get_balance_bittrex_post_details,
        EXCHANGE.KRAKEN: get_balance_kraken_post_details,
        EXCHANGE.POLONIEX: get_balance_poloniex_post_details,
        EXCHANGE.BINANCE: get_balance_binance_post_details
    }[exchange_id]


def get_balance_constructor_by_exchange_id(exchange_id):
    return {
        EXCHANGE.BITTREX: get_balance_bittrex_result_processor,
        EXCHANGE.KRAKEN: get_balance_kraken_result_processor,
        EXCHANGE.POLONIEX: get_balance_poloniex_result_processor,
        EXCHANGE.BINANCE: get_balance_binance_result_processor
    }[exchange_id]


def update_balance_by_exchange(exchange_id, cache=get_cache()):
    status_code, balance = get_balance_by_exchange(exchange_id)
    exchange_name = get_exchange_name_by_id(exchange_id)
    if status_code == STATUS.SUCCESS:
        cache.update_balance(exchange_name, balance)
        return balance
    else:
        msg = "Can't update balance for exchange_id = {exch1} {exch_name}".format(exch1=exchange_id,
                                                                                            exch_name=exchange_name)
        log_to_file(msg, "cache.log")

    return None


def get_balance(self, exchange_id, cache=get_cache()):
    exchange_name = get_exchange_name_by_id(exchange_id)
    balance = cache.get_balance(exchange_id)
    if balance is None :
        balance = self.update_balance_by_exchange(exchange_id)
        if balance is None:
            msg = "ERROR: BALANCE IS STILL NONE!!! for {n}".format(n=exchange_name)
            print_to_console(msg, LOG_ALL_ERRORS)

        return balance


def init_balances(exchanges_ids, cache=get_cache()):
    for exchange_id in exchanges_ids:
        update_balance_by_exchange(exchange_id, cache)