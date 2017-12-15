import sys
from core.base_math import get_all_permutation_list
from deploy.screen_utils import create_screen, create_screen_window, run_command_in_screen
from utils.exchange_utils import get_exchange_id_by_name, get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id, get_pair_id_by_name
from enums.deal_type import DEAL_TYPE, get_deal_type_by_id
from data.BaseData import BaseData
from collections import defaultdict


import ConfigParser

FULL_COMMAND = "python /Users/kruglovdmitry/crypto_crawler/arbitrage_between_pair.py"


def generate_screen_name(sell_exchange_id, buy_exchange_id, deal_type_id):
    screen_name = "{sell_exch}==>{buy_exch} ::: {deal_type}".format(sell_exch=get_exchange_name_by_id(sell_exchange_id),
                                                                    buy_exch=get_exchange_name_by_id(buy_exchange_id),
                                                                    deal_type=get_deal_type_by_id(deal_type_id))
    return screen_name


class DeployUnit(BaseData):
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


class ExchangeArbitrageSettings(BaseData):
    def __init__(self, src_exchange_name, dst_exchange_name, list_of_pairs):
        self.src_exchange_name = src_exchange_name
        self.src_exchange_id = get_exchange_id_by_name(self.src_exchange_name)
        self.dst_exchange_name = dst_exchange_name
        self.dst_exchange_id = get_exchange_id_by_name(self.dst_exchange_name)
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

        exchanges_ids = [exchange_id]

        for settings in exchange_settings[exchange_id]:
            dst_exchanges_id = settings.dst_exchange_id
            exchanges_ids.append(dst_exchanges_id)

        exchange_pairs = get_all_permutation_list(exchanges_ids, 2)

        for sell_exchange_id, buy_exchange_id in exchange_pairs:
            print sell_exchange_id, buy_exchange_id

            for mode_id in [DEAL_TYPE.ARBITRAGE, DEAL_TYPE.REVERSE]:

                screen_name = generate_screen_name(sell_exchange_id, buy_exchange_id, mode_id)

                current_threshold = {DEAL_TYPE.ARBITRAGE: arbitrage_threshold,
                                     DEAL_TYPE.REVERSE: balance_adjust_threshold}.get(mode_id)

                commands_per_screen = []

                for bbb in exchange_settings[exchange_id]:
                    if bbb.dst_exchange_id == sell_exchange_id or \
                            bbb.dst_exchange_id == buy_exchange_id:
                        list_of_pairs = bbb.list_of_pairs
                        for every_pair_name in list_of_pairs:
                            pair_id = get_pair_id_by_name(every_pair_name)
                            commands_per_screen.append(DeployUnit(sell_exchange_id, buy_exchange_id, pair_id, current_threshold, mode_id))

                deploy_units[screen_name] = commands_per_screen

    # Create named screen
    for screen_name in deploy_units:
        print screen_name
        create_screen(screen_name)

        for deploy_unit in deploy_units[screen_name]:
            print deploy_unit
            window_name = deploy_unit.generate_window_name()
            create_screen_window(screen_name, window_name)
            run_command_in_screen(screen_name, window_name, deploy_unit.generate_command(FULL_COMMAND))

