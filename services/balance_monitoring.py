import argparse

from dao.balance_utils import update_balance_by_exchange, init_balances
from data_access.message_queue import get_message_queue, DEAL_INFO_MSG
from data_access.memory_cache import connect_to_cache
from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, LOG_ALL_ERRORS, LOG_ALL_DEBUG
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_id_by_name, get_exchange_name_by_id
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from utils.time_utils import sleep_for, get_now_seconds_utc


# FIXME NOTE read it from settings
BITCOIN_ALARM_THRESHOLD = 0.1
TIMEOUT_HEALTH_CHECK = 60
MAX_EXPIRE_TIMEOUT = 59
POLL_TIMEOUT = 3


def log_wrong_exchange_id(exchange_id):
    msg = "UNKNOWN exchange id provided - {idx}".format(idx=exchange_id)
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, "balance.log")


def log_initial_settings(exchanges_ids):
    msg = "Starting balance monitoring for following exchanges: \n"
    for exchange_id in exchanges_ids:
        msg += str(exchange_id) + " - " + get_exchange_name_by_id(exchange_id) + "\n"
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, "balance.log")


def log_not_enough_bitcoins(exchange_id, res, msg_queue):
    msg = """           <b> !!! INFO !!! </b>
                    BTC balance on exchange {exch} BELOW threshold {thrs} - only {am} LEFT!""".format(
        thrs=BITCOIN_ALARM_THRESHOLD, exch=get_exchange_name_by_id(exchange_id), am=res.get_bitcoin_balance())
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    print_to_console(msg, LOG_ALL_ERRORS)
    print_to_console(res, LOG_ALL_MARKET_RELATED_CRAP)


def log_warn_balance_not_updating(last_balance, msg_queue):
    msg = """           <b> !!! WARNING !!! </b>
    BALANCE were not updated for a {tm} seconds!
    last balance {bl}""".format(tm=MAX_EXPIRE_TIMEOUT, bl=last_balance)

    print_to_console(msg, LOG_ALL_ERRORS)
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    log_to_file(msg, "balance.log")


def log_balance_heart_beat(idx, balance):
    msg = """Updated balance sucessfully for exch={exch}:
    {balance}""".format(exch=get_exchange_name_by_id(idx), balance=balance)
    print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)
    log_to_file(msg, "balance.log")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Balance monitoring service, every {POLL_TIMEOUT} for configured via "
                                                 "--exchanges_ids comma-separated list of exchange names ".format(POLL_TIMEOUT=POLL_TIMEOUT))

    parser.add_argument('--exchanges', action='store', required=True)

    results = parser.parse_args()

    ids_list = [x.strip() for x in results.exchanges.split(',') if x.strip()]

    exchanges_ids = []
    for exchange_name in ids_list:
        new_exchange_id = get_exchange_id_by_name(exchange_name)
        if new_exchange_id in EXCHANGE.values():
            exchanges_ids.append(new_exchange_id)
        else:
            log_wrong_exchange_id(exchanges_id)
            raise

    log_initial_settings(exchanges_ids)

    cache = connect_to_cache()
    msg_queue = get_message_queue()

    load_keys("./secret_keys")
    init_balances(exchanges_ids, cache)

    cnt = 0

    while True:
        # We load initial balance using init_balance
        sleep_for(POLL_TIMEOUT)

        cnt += POLL_TIMEOUT

        for idx in exchanges_ids:
            tr = "Updating for exch = {exch}".format(exch=get_exchange_name_by_id(idx))
            print_to_console(tr, LOG_ALL_DEBUG)

            res = update_balance_by_exchange(idx, cache)
            while res is None:
                print_to_console("Balance is NONE:", LOG_ALL_MARKET_RELATED_CRAP)
                sleep_for(1)
                res = update_balance_by_exchange(idx, cache)

            if not res.do_we_have_enough_bitcoin(BITCOIN_ALARM_THRESHOLD):
                log_not_enough_bitcoins(idx, res, msg_queue)

        if cnt >= TIMEOUT_HEALTH_CHECK:
            cnt = 0
            timest = get_now_seconds_utc()
            print "At ts={ts} what we have at cache".format(ts=timest)
            for idx in exchanges_ids:
                some_balance = cache.get_balance(idx)
                if some_balance is None or (timest - some_balance.last_update) > MAX_EXPIRE_TIMEOUT:
                    log_warn_balance_not_updating(some_balance, msg_queue)
                else:
                    log_balance_heart_beat(idx, some_balance)
