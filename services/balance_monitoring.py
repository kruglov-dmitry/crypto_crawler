import argparse

from dao.balance_utils import update_balance_by_exchange, init_balances
from data_access.message_queue import get_message_queue
from data_access.memory_cache import connect_to_cache
from enums.exchange import EXCHANGE
from utils.exchange_utils import get_exchange_id_by_name
from services.balance_monitoring_logging import log_wrong_exchange_id, log_initial_settings, \
    log_balance_update_heartbeat, log_cant_update_balance, log_last_balances, log_not_enough_base_currency

from utils.key_utils import load_keys
from utils.time_utils import sleep_for

from enums.currency import CURRENCY
from constants import BASE_CURRENCY, BASE_CURRENCIES_BALANCE_THRESHOLD



TIMEOUT_HEALTH_CHECK = 180
POLL_TIMEOUT = 3


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
            log_wrong_exchange_id(new_exchange_id)

            assert new_exchange_id in EXCHANGE.values()

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

        for exchange_id in exchanges_ids:
            log_balance_update_heartbeat(exchange_id)

            balance_for_exchange = update_balance_by_exchange(exchange_id, cache)
            while balance_for_exchange is None:
                log_cant_update_balance(exchange_id)
                sleep_for(1)
                balance_for_exchange = update_balance_by_exchange(exchange_id, cache)

            for base_currency_id in BASE_CURRENCY:
                threshold = BASE_CURRENCIES_BALANCE_THRESHOLD[base_currency_id]
                if not balance_for_exchange.do_we_have_enough(base_currency_id, threshold):
                    log_not_enough_base_currency(exchange_id, base_currency_id, threshold, balance_for_exchange, msg_queue)

        if cnt >= TIMEOUT_HEALTH_CHECK:
            cnt = 0
            log_last_balances(exchanges_ids, cache, msg_queue)
