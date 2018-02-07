from debug_utils import print_to_console, LOG_ALL_ERRORS

from deploy.screen_utils import create_screen, create_screen_window, run_command_in_screen
from deploy.constants import TELEGRAM_NOTIFIER_DEPLOY_UNIT, BALANCE_UPDATE_DEPLOY_UNIT, TRADE_SAVING_DEPLOY_UNIT, \
    EXPIRED_ORDER_PROCESSING_DEPLOY_UNIT, FAILED_ORDER_PROCESSING_DEPLOY_UNIT


def deploy_telegram_notifier(screen_name=TELEGRAM_NOTIFIER_DEPLOY_UNIT.screen_name, should_create_screen=False):
    print_to_console("Initialization of telegram notification service...", LOG_ALL_ERRORS)
    if should_create_screen:
        create_screen(screen_name)
    create_screen_window(screen_name, TELEGRAM_NOTIFIER_DEPLOY_UNIT.window_name)
    run_command_in_screen(screen_name, TELEGRAM_NOTIFIER_DEPLOY_UNIT.window_name,
                          TELEGRAM_NOTIFIER_DEPLOY_UNIT.command)


def deploy_trade_storing(screen_name=TRADE_SAVING_DEPLOY_UNIT.screen_name, should_create_screen=False):
    print_to_console("Initialization of trade saving service...", LOG_ALL_ERRORS)
    if should_create_screen:
        create_screen(screen_name)
    create_screen_window(screen_name, TRADE_SAVING_DEPLOY_UNIT.window_name)
    run_command_in_screen(screen_name, TRADE_SAVING_DEPLOY_UNIT.window_name,
                          TRADE_SAVING_DEPLOY_UNIT.command)


def deploy_expired_order_processing(screen_name=EXPIRED_ORDER_PROCESSING_DEPLOY_UNIT.screen_name, should_create_screen=False):
    print_to_console("Initialization of expired order processing service...", LOG_ALL_ERRORS)
    if should_create_screen:
        create_screen(screen_name)
    create_screen_window(screen_name, EXPIRED_ORDER_PROCESSING_DEPLOY_UNIT.window_name)
    run_command_in_screen(screen_name, EXPIRED_ORDER_PROCESSING_DEPLOY_UNIT.window_name,
                          EXPIRED_ORDER_PROCESSING_DEPLOY_UNIT.command)


def deploy_failed_order_processing(screen_name=FAILED_ORDER_PROCESSING_DEPLOY_UNIT.screen_name, should_create_screen=False):
    print_to_console("Initialization of failed order processing service...", LOG_ALL_ERRORS)
    if should_create_screen:
        create_screen(screen_name)
    create_screen_window(screen_name, FAILED_ORDER_PROCESSING_DEPLOY_UNIT.window_name)
    run_command_in_screen(screen_name, FAILED_ORDER_PROCESSING_DEPLOY_UNIT.window_name,
                          FAILED_ORDER_PROCESSING_DEPLOY_UNIT.command)


def deploy_process_in_screen(screen_name, deploy_unit, should_create_window=True):
    """
        Will create new named window in EXISTING screen `screen_name`
        and run there command according to deploy unit

    :param screen_name:
    :param deploy_unit: type: DeployUnit
    :return:
    """
    msg = """Executing {smd} in screen_name = {s_n}. New window {wn} will be created: {tf}""".format(
        smd=deploy_unit.command, s_n=screen_name, wn=deploy_unit.window_name, tf=should_create_window)
    print_to_console(msg, LOG_ALL_ERRORS)

    if should_create_window:
        create_screen_window(screen_name, deploy_unit.window_name)

    run_command_in_screen(screen_name, deploy_unit.window_name, deploy_unit.command)


def deploy_balance_monitoring(command_to_execute, screen_name=BALANCE_UPDATE_DEPLOY_UNIT.screen_name, should_create_screen=False):
    print_to_console("Initialization of balance monitoring service...", LOG_ALL_ERRORS)
    if should_create_screen:
        create_screen(screen_name)
    create_screen_window(screen_name, BALANCE_UPDATE_DEPLOY_UNIT.window_name)
    run_command_in_screen(screen_name, BALANCE_UPDATE_DEPLOY_UNIT.window_name, command_to_execute)