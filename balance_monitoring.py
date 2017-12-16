from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.file_utils import log_to_file
from data_access.memory_cache import connect_to_cache
from enums.exchange import EXCHANGE
from dao.balance_utils import update_balance_by_exchange, init_balances
from utils.key_utils import load_keys

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
        sleep_for(POLL_TIMEOUT)

        cnt += POLL_TIMEOUT

        for idx in exchanges_ids:
            print "Update for ", idx
            update_balance_by_exchange(idx, cache)

        print cnt

        if cnt >= TIMEOUT_HEALTH_CHECK:
            cnt = 0
            timest = get_now_seconds_utc()
            print "At ts={ts} what we have at cachec".format(ts=timest)
            for idx in exchanges_ids:
                some_balance = cache.get_balance(idx)
                if some_balance is None or (timest - some_balance.last_update) > MAX_EXPIRE_TIMEOUT:
                    msg = "<<<< ERROR >>>> BALANCE were not updated for a {tm} seconds ".format(tm=MAX_EXPIRE_TIMEOUT)
                    print msg
                    log_to_file(msg, "cache.log")
                else:
                    print some_balance