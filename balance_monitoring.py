from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.file_utils import log_to_file
from utils.key_utils import load_keys
from debug_utils import print_to_console, LOG_ALL_MARKET_RELATED_CRAP, LOG_ALL_ERRORS, LOG_ALL_DEBUG
from utils.exchange_utils import get_exchange_name_by_id

from data_access.memory_cache import connect_to_cache
from data_access.telegram_notifications import send_single_message

from enums.exchange import EXCHANGE
from enums.notifications import NOTIFICATION

from dao.balance_utils import update_balance_by_exchange, init_balances

BITCOIN_ALARM_THRESHOLD = 0.1

if __name__ == "__main__":

    # FIXME use config from deploy here
    exchanges_ids = [EXCHANGE.BITTREX, EXCHANGE.POLONIEX, EXCHANGE.BINANCE]

    print "Starting balance monitoring for following exchanges"
    print exchanges_ids

    cache = connect_to_cache()

    load_keys("./secret_keys")
    init_balances(exchanges_ids, cache)

    TIMEOUT_HEALTH_CHECK = 60
    MAX_EXPIRE_TIMEOUT = 59
    POLL_TIMEOUT = 10
    cnt = 0

    while True:
        # We load initial balance using init_balance
        sleep_for(POLL_TIMEOUT)

        cnt += POLL_TIMEOUT

        for idx in exchanges_ids:
            tr = "Updating for exch = {exch}".format(exch=get_exchange_name_by_id(idx))
            print_to_console(tr, LOG_ALL_DEBUG)

            res = update_balance_by_exchange(idx, cache)

            if res.do_we_have_enough_bitcoin(BITCOIN_ALARM_THRESHOLD):
                msg = """           <b> !!! INFO !!! </b>
                BTC balance on exchange {exch} BELOW threshold {thrs} - only {am} LEFT!""".format(
                    thrs=BITCOIN_ALARM_THRESHOLD, exch=get_exchange_name_by_id(idx), am=res.get_bitcoin_balance())
                send_single_message(msg, NOTIFICATION.DEAL)
                print_to_console(msg, LOG_ALL_MARKET_RELATED_CRAP)

        if cnt >= TIMEOUT_HEALTH_CHECK:
            cnt = 0
            timest = get_now_seconds_utc()
            print "At ts={ts} what we have at cachec".format(ts=timest)
            for idx in exchanges_ids:
                some_balance = cache.get_balance(idx)
                if some_balance is None or (timest - some_balance.last_update) > MAX_EXPIRE_TIMEOUT:
                    msg = """           <b> <<<< WARNING >>>> </b> 
                    BALANCE were not updated for a {tm} seconds!
                    last balance {bl}""".format(tm=MAX_EXPIRE_TIMEOUT, bl=some_balance)
                    print_to_console(msg, LOG_ALL_ERRORS)
                    send_single_message(msg, NOTIFICATION.DEAL)
                    log_to_file(msg, "balance.log")
                else:
                    msg = """Updated balance sucessfully for exch={exch}:
                    {balance}
                    """.format(exch=get_exchange_name_by_id(idx), balance= some_balance)
                    print_to_console(some_balance, LOG_ALL_MARKET_RELATED_CRAP)
                    log_to_file(some_balance, "balance.log")