from utils.time_utils import sleep_for, get_now_seconds_utc
from utils.file_utils import log_to_file
from data_access.memory_cache import local_cache
from enums.exchange import EXCHANGE


if __name__ == "__main__":

    exchanges_ids = [EXCHANGE.BITTREX, EXCHANGE.POLONIEX, EXCHANGE.BINANCE]
    local_cache.init_balances(exchanges_ids)

    TIMEOUT_HEALTH_CHECK = 60
    MAX_EXPIRE_TIMEOUT = 59
    cnt = 0

    while True:
        sleep_for(1)
        cnt += 1
        for idx in exchanges_ids:
            local_cache.update_balance_by_exchange(idx)

        if cnt == TIMEOUT_HEALTH_CHECK:
            cnt = 0
            timest = get_now_seconds_utc()
            for idx in exchanges_ids:
                some_balance = local_cache.get_balance(idx)
                if some_balance is None or (timest - some_balance.last_update) > MAX_EXPIRE_TIMEOUT:
                    msg = "<<<< ERROR >>>> BALANCE were not updated for a {tm} seconds ".format(tm=MAX_EXPIRE_TIMEOUT)
                    print msg
                    log_to_file(msg, "cache.log")