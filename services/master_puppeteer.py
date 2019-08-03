import argparse
from utils.time_utils import sleep_for
from deploy.classes.common_settings import CommonSettings
from data_access.classes.command_queue import CommandQueue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Core management unit responsible for re-spawning arbitrage process and updating configuration
    """)

    parser.add_argument('--cfg', action='store', required=True)
    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    command_queue = CommandQueue(settings.cache_host, settings.cache_port)

    nodes = []

    while True:
        nodes = command_queue.get_list_of_nodes()

        for node in nodes:
            # reflect nodes within dashboard
            # i.e. register complete servers that should contains
            pass

        sleep_for(1)