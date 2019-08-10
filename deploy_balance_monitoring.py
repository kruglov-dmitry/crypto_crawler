import argparse

from utils.debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.exchange_utils import get_exchange_name_by_id

from deploy.classes.common_settings import CommonSettings
from deploy.classes.deploy_unit import DeployUnit
from deploy.service_utils import deploy_process_in_screen
from deploy.constants import BALANCE_UPDATE_DEPLOY_UNIT
from deploy.screen_utils import create_screen


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Balance monitoring service, every {POLL_TIMEOUT} for configured via "
                                                 "--cfg file containing core settings")
    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    print_to_console("1 stage - create named screen for balance retrieval...", LOG_ALL_ERRORS)
    create_screen(BALANCE_UPDATE_DEPLOY_UNIT.screen_name)

    print_to_console("2 stage - init balance retrieval per exchange...", LOG_ALL_ERRORS)
    for exchange_id in settings.exchanges:
        deploy_unit = DeployUnit(BALANCE_UPDATE_DEPLOY_UNIT.screen_name,
                                 get_exchange_name_by_id(exchange_id),
                                 BALANCE_UPDATE_DEPLOY_UNIT.command + get_exchange_name_by_id(exchange_id))

        deploy_process_in_screen(BALANCE_UPDATE_DEPLOY_UNIT.screen_name, deploy_unit, should_create_window=True)
