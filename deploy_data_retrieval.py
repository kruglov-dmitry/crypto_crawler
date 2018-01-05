from deploy.screen_utils import create_screen, create_screen_window, run_command_in_screen, generate_screen_name
from deploy.constants import DATA_RETRIEVAL_SERVICES, TELEGRAM_NOTIFIER_DEPLOY_UNIT

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.time_utils import sleep_for


if __name__ == "__main__":
    # FIXME NOTE: read settings from cfg

    print_to_console("1 stage - init telegram notification service...", LOG_ALL_ERRORS)
    create_screen(TELEGRAM_NOTIFIER_DEPLOY_UNIT.screen_name)
    create_screen_window(TELEGRAM_NOTIFIER_DEPLOY_UNIT.screen_name, TELEGRAM_NOTIFIER_DEPLOY_UNIT.window_name)
    run_command_in_screen(TELEGRAM_NOTIFIER_DEPLOY_UNIT.screen_name, TELEGRAM_NOTIFIER_DEPLOY_UNIT.window_name, TELEGRAM_NOTIFIER_DEPLOY_UNIT.command)
    sleep_for(3)

    print_to_console("2 stage - init data retrieval services...", LOG_ALL_ERRORS)
    for deploy_unit in DATA_RETRIEVAL_SERVICES.values():
        print_to_console("Executing " + deploy_unit.command, LOG_ALL_ERRORS)
        create_screen_window(deploy_unit.screen_name, deploy_unit.window_name)
        run_command_in_screen(deploy_unit.screen_name, deploy_unit.window_name, deploy_unit.command)