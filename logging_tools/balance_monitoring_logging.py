from utils.debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, LOG_ALL_ERRORS, LOG_ALL_DEBUG
from utils.file_utils import log_to_file
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import get_now_seconds_utc
from utils.currency_utils import get_currency_name_by_id

from data_access.message_queue import DEAL_INFO_MSG

BALANCE_EXPIRE_TIMEOUT = 179


def log_initial_settings(msg, exchanges_ids):
    for exchange_id in exchanges_ids:
        msg += str(exchange_id) + " - " + get_exchange_name_by_id(exchange_id) + "\n"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, "balance.log")


def log_not_enough_base_currency(exchange_id, currency_id, threshold, balance_for_exchange, msg_queue):
    msg = """<b> !!! INFO !!! </b>
    {base_currency} balance on exchange {exch} BELOW threshold {thrs} - only {am} LEFT!""".format(
        base_currency=get_currency_name_by_id(currency_id),
        thrs=threshold, exch=get_exchange_name_by_id(exchange_id), am=balance_for_exchange.get_balance(currency_id))
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    print_to_console(balance_for_exchange, LOG_ALL_MARKET_RELATED_CRAP)
    log_to_file(str(balance_for_exchange), "balance.log")


def log_warn_balance_not_updating(last_balance, msg_queue):
    msg = """           <b> !!! WARNING !!! </b>
    BALANCE were not updated for a {tm} seconds!
    last balance {bl}""".format(tm=BALANCE_EXPIRE_TIMEOUT, bl=last_balance)

    print_to_console(msg, LOG_ALL_ERRORS)
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    log_to_file(msg, "balance.log")


def log_balance_updated(idx, balance):
    msg = """Updated balance sucessfully for exch={exch}:
    {balance}""".format(exch=get_exchange_name_by_id(idx), balance=balance)
    print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
    log_to_file(msg, "balance.log")


def log_last_balances(exchanges_ids, cache, msg_queue):
    timest = get_now_seconds_utc()
    ttl = "At ts={ts} what we have at cache".format(ts=timest)
    print_to_console(ttl, LOG_ALL_ERRORS)
    log_to_file(ttl, "balance.log")
    for idx in exchanges_ids:
        some_balance = cache.get_balance(idx)
        if some_balance is None or (timest - some_balance.last_update) > BALANCE_EXPIRE_TIMEOUT:
            log_warn_balance_not_updating(some_balance, msg_queue)
        else:
            log_balance_updated(idx, some_balance)


def log_cant_update_balance(idx):
    msg = "Balance is NONE for exchange {exch}. Will retry in 1 second...".format(exch=get_exchange_name_by_id(idx))
    print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
    log_to_file(msg, "balance.log")


def log_balance_update_heartbeat(idx):
    tr = "Updating for exch = {exch}".format(exch=get_exchange_name_by_id(idx))
    print_to_console(tr, LOG_ALL_DEBUG)
    log_to_file(tr, "balance.log")