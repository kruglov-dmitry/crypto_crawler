from debug_utils import LOG_ALL_ERRORS, print_to_console
from utils.file_utils import log_to_file
from utils.exchange_utils import get_exchange_name_by_id
from data_access.message_queue import DEAL_INFO_MSG
from constants import BALANCE_EXPIRED_THRESHOLD


def log_balance_expired_errors(cfg, msg_queue, balance_state):
    msg = """<b> !!! CRITICAL !!! </b>
    Balance is OUTDATED for {exch1} or {exch2} for more than {tt} seconds
    Arbitrage process will be stopped just in case.
    Check log file: {lf}""".format(exch1=get_exchange_name_by_id(cfg.buy_exchange_id),
                                   exch2=get_exchange_name_by_id(cfg.sell_exchange_id),
                                   tt=BALANCE_EXPIRED_THRESHOLD, lf=cfg.log_file_name)
    print_to_console(msg, LOG_ALL_ERRORS)
    msg_queue.add_message(DEAL_INFO_MSG, msg)
    log_to_file(msg, cfg.log_file_name)
    log_to_file(balance_state, cfg.log_file_name)


def log_failed_to_retrieve_order_book(cfg):
    msg = "CAN'T retrieve order book for {nn} or {nnn}".format(nn=get_exchange_name_by_id(cfg.sell_exchange_id),
                                                               nnn=get_exchange_name_by_id(cfg.buy_exchange_id))
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)


def log_dont_supported_currency(cfg, exchange_id, pair_id):
    msg = "Not supported currency {idx}-{name} for {exch}".format(idx=cfg.pair_id, name=pair_id,
                                                                  exch=get_exchange_name_by_id(exchange_id))
    print_to_console(msg, LOG_ALL_ERRORS)
    log_to_file(msg, cfg.log_file_name)