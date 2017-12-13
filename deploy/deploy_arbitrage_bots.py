import sys
from core.base_math import get_all_permutation_list
from deploy.screen_utils import create_screen, create_screen_window, run_command_in_screen
from utils.exchange_utils import get_exchange_id_by_name, get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id
from enums.deal_type import DEAL_TYPE, get_deal_type_by_id

import json
import ConfigParser


def generate_screen_name(sell_exchange_id, buy_exchange_id, deal_type_id):
    screen_name = "{sell_exch}==>{buy_exch} ::: {deal_type}".format(sell_exch=get_exchange_name_by_id(sell_exchange_id),
                                                                    buy_exch=get_exchange_name_by_id(buy_exchange_id),
                                                                    deal_type=get_deal_type_by_id(deal_type_id))
    return screen_name


class DeployUnit:
    def __init__(self, sell_exchange_id, buy_exchange_id, pair_id, threshold, mode_id):
        self.threshold = threshold
        self.sell_exchange_id = sell_exchange_id
        self.buy_exchange_id = buy_exchange_id
        self.pair_id = pair_id
        self.mode_id = mode_id

    def generate_window_name(self):
        window_name = "{pair_id} - {pair_name}".format(pair_id=self.pair_id,pair_name=get_pair_name_by_id(self.pair_id))
        return window_name

    def generate_command(self, full_path_to_script):
        cmd = "{cmd} --threshold {threshold} --sell_exchange_id {sell_exchange_id} --buy_exchange_id {buy_exchange_id} " \
              "--pair_id {pair_id} --mode_id {mode_id}".format(
            cmd=full_path_to_script,
            threshold=self.threshold,
            sell_exchange_id=self.sell_exchange_id,
            buy_exchange_id=self.buy_exchange_id,
            pair_id=self.pair_id,
            mode_id=self.mode_id)

        return cmd


class ExchangeArbitrageSettings:
    def __init__(self, exchange_name, list_of_other_exchanges, list_of_pairs):
        self.exchange_name = exchange_name
        self.trade_with = list_of_other_exchanges
        self.list_of_pairs = list_of_pairs


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

    exchanges = json.loads(config.get("common","exchanges"))

    exchange_settings = {}
    for exchange_name in exchanges:
        exchange_id = get_exchange_id_by_name(exchange_name.upper())

        trade_with = json.loads(config.get(exchange_name,"exchanges"))
        pairs = json.loads(config.get(exchange_name, "exchanges"))

        exchange_settings[exchange_id] = ExchangeArbitrageSettings(exchange_name, trade_with, pairs)

    deploy_units = {}

    for exchange_id in exchange_settings:

        exchanges_ids = map(get_exchange_id_by_name, exchange_settings[exchange_id].trade_with)
        exchanges_ids.append(exchange_id)

        exchange_pairs = get_all_permutation_list(exchanges_ids, 2)

        for sell_exchange_id, buy_exchange_id in exchange_pairs:
            for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:

                screen_name = generate_screen_name(sell_exchange_id, buy_exchange_id, mode_id)

                current_threshold = {DEAL_TYPE.ARBITRAGE: arbitrage_threshold,
                                     DEAL_TYPE.REVERSE: balance_adjust_threshold}.get(mode_id)

                commands_per_screen = []

                for every_pair in exchange_settings[exchange_id].list_of_pairs:
                    commands_per_screen.append(DeployUnit(sell_exchange_id, buy_exchange_id, every_pair, current_threshold, mode_id))

                deploy_units[screen_name] = commands_per_screen

    # Create named screen
    for screen_name in deploy_units:
        create_screen(screen_name)
        for deploy_unit in deploy_units:
            window_name = deploy_unit.generate_window_name()
            create_screen_window(screen_name, window_name)
            run_command_in_screen(screen_name, window_name, deploy_unit.generate_command())

