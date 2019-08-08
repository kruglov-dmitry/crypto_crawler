import socket
import argparse

from utils.time_utils import sleep_for
from debug_utils import print_to_console, LOG_ALL_DEBUG
from deploy.classes.common_settings import CommonSettings
from data_access.classes.command_queue import CommandQueue


def register_and_wait_for_commands(args):
    settings = CommonSettings.from_cfg(args.cfg)

    command_queue = CommandQueue(settings.cache_host, settings.cache_port)

    #
    # while true read settings
    #   1) what kind of services to deploy
    #   2) service specific settings
    #

    server_name = socket.gethostname()
    command_queue.register_node(server_name)

    while True:
        # get command
        # execute

        cmd = command_queue.get_command()
        if cmd:
            print_to_console("Subscriber: {} - {}".format(server_name, cmd), LOG_ALL_DEBUG)
        sleep_for(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    It will be deployed to every node to 
        1. Register within dashboard
        2. Send heartbeat to msg queue to reflect that agent is active at this node 
        3. watch for commands to deploy\stop\\reconfigure all services at this node  
    """)

    parser.add_argument('--cfg', action='store', required=True)
    arguments = parser.parse_args()

    register_and_wait_for_commands(arguments)