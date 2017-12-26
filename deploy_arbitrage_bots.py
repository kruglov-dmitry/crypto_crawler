import sys
from collections import defaultdict
import ConfigParser

from deploy.screen_utils import create_screen, create_screen_window, run_command_in_screen, generate_screen_name
from deploy.constants import FULL_COMMAND, BALANCE_UPDATE_COMMAND, BALANCE_SCREEN_NAME, BALANCE_WINDOW_NAME
from deploy.ExchangeArbitrageSettings import ExchangeArbitrageSettings

from utils.exchange_utils import get_exchange_id_by_name, get_exchange_name_by_id
from utils.currency_utils import get_pair_id_by_name
from utils.time_utils import sleep_for
from debug_utils import get_logging_level_id_by_name

from data.ArbitrageConfig import ArbitrageConfig


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: {prg_name} your_config.cfg".format(prg_name=sys.argv[0])
        print "FIXME TODO: we should use argparse module"
        exit(0)

    cfg_file_name = sys.argv[1]

    config = ConfigParser.RawConfigParser()
    config.read(cfg_file_name)

    arbitrage_threshold = config.get("common", "arbitrage_threshold")
    balance_adjust_threshold = config.get("common", "balance_adjust_threshold")
    logging_level_name = config.get("common", "log_level")

    exchanges = [x.strip() for x in config.get("common","exchanges").split(",") if len(x.strip()) > 0]

    exchange_settings = defaultdict(list)

    for exchange_name in exchanges:
        exchange_id = get_exchange_id_by_name(exchange_name)
        trade_with = [x.strip() for x in config.get(exchange_name,"exchanges").split(",") if len(x.strip()) > 0]
        if len(trade_with) == 0:
            continue
        for dst_exchange_name in trade_with:
            pairs = [x.strip() for x in config.get(exchange_name, dst_exchange_name).split(",") if len(x.strip()) > 0]
            if len(pairs) > 0:
                exchange_settings[exchange_id].append(ExchangeArbitrageSettings(exchange_name, dst_exchange_name, pairs))

    for b in exchange_settings:
        print b, get_exchange_name_by_id(b)
        for x in exchange_settings[b]:
            print x

    deploy_units = {}

    for exchange_id in exchange_settings:

        for settings in exchange_settings[exchange_id]:
            dst_exchanges_id = settings.dst_exchange_id

            exchange_pairs = [[exchange_id, dst_exchanges_id], [dst_exchanges_id, exchange_id]]

            for sell_exchange_id, buy_exchange_id in exchange_pairs:

                screen_name = generate_screen_name(sell_exchange_id, buy_exchange_id)

                commands_per_screen = []

                list_of_pairs = settings.list_of_pairs
                for every_pair_name in list_of_pairs:
                    pair_id = get_pair_id_by_name(every_pair_name)
                    commands_per_screen.append(ArbitrageConfig(sell_exchange_id, buy_exchange_id, pair_id,
                                                               arbitrage_threshold, balance_adjust_threshold,
                                                               get_logging_level_id_by_name(logging_level_name)))
                    deploy_units[screen_name] = commands_per_screen

    # Create named screen
    # 1st stage - initialization balance polling service
    create_screen(BALANCE_SCREEN_NAME)
    create_screen_window(BALANCE_SCREEN_NAME, BALANCE_WINDOW_NAME)
    run_command_in_screen(BALANCE_SCREEN_NAME, BALANCE_WINDOW_NAME, BALANCE_UPDATE_COMMAND)

    # Let it update balance first
    sleep_for(5)

    # 2nd stage - spawn a shit load of arbitrage checkers
    for screen_name in deploy_units:
        create_screen(screen_name)

        for deploy_unit in deploy_units[screen_name]:
            window_name = deploy_unit.generate_window_name()
            create_screen_window(screen_name, window_name)
            run_command_in_screen(screen_name, window_name, deploy_unit.generate_command(FULL_COMMAND))
