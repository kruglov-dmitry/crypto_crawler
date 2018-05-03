import argparse

from deploy.classes.CommonSettings import CommonSettings

from dao.balance_utils import update_balance_by_exchange, init_balances
from data_access.message_queue import get_message_queue
from data_access.memory_cache import connect_to_cache
from logging_tools.balance_monitoring_logging import log_initial_settings, log_balance_update_heartbeat, \
    log_cant_update_balance, log_last_balances, log_not_enough_base_currency
from debug_utils import set_log_folder, set_logging_level

from utils.key_utils import load_keys
from utils.time_utils import sleep_for

from constants import BASE_CURRENCY, BASE_CURRENCIES_BALANCE_THRESHOLD

TIMEOUT_HEALTH_CHECK = 180
POLL_TIMEOUT = 3

# FIXME NOTE - process exchange in parallel to avoid bot stoping in case one of exchanges get stuck


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Balance monitoring service, every {POLL_TIMEOUT} for configured via "
                                                 "--exchanges_ids comma-separated list of exchange names ".format(POLL_TIMEOUT=POLL_TIMEOUT))
    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    log_initial_settings("Starting balance monitoring for following exchanges: \n", settings.exchanges)

    cache = connect_to_cache(host=settings.cache_host, port=settings.cache_port)
    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)

    load_keys(settings.key_path)
    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    init_balances(settings.exchanges, cache)

    cnt = 0

    while True:
        # We load initial balance using init_balance
        sleep_for(POLL_TIMEOUT)

        cnt += POLL_TIMEOUT

        for exchange_id in settings.exchanges:
            log_balance_update_heartbeat(exchange_id)

            balance_for_exchange = update_balance_by_exchange(exchange_id, cache)
            while balance_for_exchange is None:
                log_cant_update_balance(exchange_id)
                sleep_for(1)
                balance_for_exchange = update_balance_by_exchange(exchange_id, cache)

            # for base_currency_id in BASE_CURRENCY:
            #     threshold = BASE_CURRENCIES_BALANCE_THRESHOLD[base_currency_id]
            #     if not balance_for_exchange.do_we_have_enough(base_currency_id, threshold):
            #        log_not_enough_base_currency(exchange_id, base_currency_id, threshold, balance_for_exchange, msg_queue)

        if cnt >= TIMEOUT_HEALTH_CHECK:
            cnt = 0
            log_last_balances(settings.exchanges, cache, msg_queue)
