import argparse

from deploy.classes.common_settings import CommonSettings

from dao.balance_utils import update_balance_by_exchange, init_balances
from data_access.message_queue import get_message_queue
from data_access.memory_cache import connect_to_cache
from logging_tools.balance_monitoring_logging import log_initial_settings, log_balance_update_heartbeat, \
    log_cant_update_balance, log_last_balances, log_not_enough_base_currency
from logging_tools.exchange_util_logging import log_wrong_exchange_id
from utils.debug_utils import set_log_folder, set_logging_level

from utils.key_utils import load_keys
from utils.time_utils import sleep_for
from utils.exchange_utils import get_exchange_id_by_name, EXCHANGE
from utils.system_utils import die_hard

from constants import BASE_CURRENCY, BASE_CURRENCIES_BALANCE_THRESHOLD, BALANCE_POLL_TIMEOUT, \
    BALANCE_HEALTH_CHECK_TIMEOUT


def watch_balance_for_exchange(args):
    """
            Those routine update balance at redis CACHE
            for ALL coins at ONE exchange for active key set.

            NOTE:   It still rely on REST api - i.e. not proactive
                    For some exchanges - balance not immediately updated

                    Initially all exchanges were polled sequentially
                    But it lead to delays in the past
                    due to exchange errors or throttling

    :param args: config file and exchange_id
    :return:
    """
    settings = CommonSettings.from_cfg(args.cfg)

    exchange_id = get_exchange_id_by_name(args.exchange)
    if exchange_id not in EXCHANGE.values():
        log_wrong_exchange_id(exchange_id)
        die_hard("Exchange id {} seems to be unknown? 0_o".format(exchange_id))

    log_initial_settings("Starting balance monitoring for following exchange: \n", [exchange_id])

    cache = connect_to_cache(host=settings.cache_host, port=settings.cache_port)
    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)

    load_keys(settings.key_path)
    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    init_balances(settings.exchanges, cache)

    cnt = 0

    while True:
        # We load initial balance using init_balance
        sleep_for(BALANCE_POLL_TIMEOUT)

        cnt += BALANCE_POLL_TIMEOUT

        log_balance_update_heartbeat(exchange_id)

        balance_for_exchange = update_balance_by_exchange(exchange_id, cache)
        while balance_for_exchange is None:
            log_cant_update_balance(exchange_id)
            sleep_for(1)
            balance_for_exchange = update_balance_by_exchange(exchange_id, cache)

        if cnt >= BALANCE_HEALTH_CHECK_TIMEOUT:
            cnt = 0
            log_last_balances(settings.exchanges, cache, msg_queue)

            for base_currency_id in BASE_CURRENCY:
                threshold = BASE_CURRENCIES_BALANCE_THRESHOLD[base_currency_id]
                if not balance_for_exchange.do_we_have_enough(base_currency_id, threshold):
                    log_not_enough_base_currency(exchange_id, base_currency_id, threshold,
                                                 balance_for_exchange, msg_queue)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Balance monitoring service, every {POLL_TIMEOUT} for configured via "
                    "--exchanges_ids comma-separated list of exchange names ".format(POLL_TIMEOUT=BALANCE_POLL_TIMEOUT))
    parser.add_argument('--cfg', action='store', required=True)
    parser.add_argument('--exchange', action='store', required=True)

    arguments = parser.parse_args()

    watch_balance_for_exchange(arguments)
