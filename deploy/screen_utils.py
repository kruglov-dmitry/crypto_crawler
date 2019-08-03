import re
import commands
from subprocess import check_output

from utils.exchange_utils import get_exchange_name_by_id


def is_screen_present(screen_name):
    var = check_output(["screen -ls; true"], shell=True)
    if ".{}\t(".format(screen_name) in var:
        print("Screen with name {} is running!".format(screen_name))
        return True

    print("Screen with name {} is not running".format(screen_name))
    return False


def generate_screen_name(sell_exchange_id, buy_exchange_id):
    screen_name = "{sell_exch}==>{buy_exch}".format(
        sell_exch=get_exchange_name_by_id(sell_exchange_id),
        buy_exch=get_exchange_name_by_id(buy_exchange_id))
    return screen_name


def stop_screen(screen_name):
    screen_pid = re.findall(r'\d*\.', commands.getoutput('screen -ls |grep %s' % screen_name))
    if screen_pid:
        commands.getoutput('kill %s' % screen_pid[0][:-1])


def create_screen(screen_name):
    """
    Create screen on local machine

    :param screen_name:
    :return: output if any
    """

    if is_screen_present(screen_name):
        print("NONONO! You already have with exact same name - {screen_name} "
              "It will lead to trouble.".format(screen_name=screen_name))
        assert False

    if isinstance(screen_name, str):
        out = commands.getoutput('screen -dmS "%s"' % screen_name)
        print(out)
    else:
        out = "No screen name provided"

    return out


def create_screen_window(screen_name, window_name):
    """

    Create numerous named screen consoles in screen with name screen_name

    :param screen_name:
    :param window_name:
    :return: False, if assert failed or command output
    """
    cmd = """screen -S '{screen_name}' -X screen -t '{window_name}'""".format(
        screen_name=screen_name, window_name=window_name)

    return commands.getoutput(cmd)


def run_command_in_screen(screen_name, window_name, command):
    """
    :param screen_name:
    :param window_name:
    :param command: full command with ALL arguments
    :return: command execution output if any
    """

    cmd_line = """screen -S '{sn}' -p '{wn}' -X stuff '{exe}\n' """.format(sn=screen_name, wn=window_name, exe=command)
    print("Executing command:\n{}".format(cmd_line))
    return commands.getoutput(cmd_line)


def test_screens():
    screen_name = "WTF"
    window_list = ["1", "2", "3"]
    create_screen(screen_name)
    for w in window_list:
        create_screen_window(screen_name, w)

    run_command_in_screen(screen_name, "1", "ls -la")
    run_command_in_screen(screen_name, "2", "netstat -tunapl")
    run_command_in_screen(screen_name, "3", "htop")
