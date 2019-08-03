import socket
import argparse
from utils.time_utils import sleep_for
from deploy.classes.CommonSettings import CommonSettings
from data_access.classes.command_queue import CommandQueue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Core management unit responsible for re-spawning arbitrage process and updating configuration
    """)

    parser.add_argument('--cfg', action='store', required=True)
    arguments = parser.parse_args()

    settings = CommonSettings.from_cfg(arguments.cfg)

    command_queue = CommandQueue(settings.cache_host, settings.cache_port)

    #
    # whilte true read settings
    #   1) what kind of services to deploy
    #   2) service specific settings

    server_name = socket.gethostname()
    command_queue.register_node(server_name)

    # p = r.pubsub()
    # p.subscribe('test')

    puppets = []

    while True:
        # get command
        # execute

        cmd = command_queue.get_command()
        if cmd:
            print "Subscriber: %s" % cmd
        sleep_for(1)