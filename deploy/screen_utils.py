import re, commands


def stop_screen(screen_name):
    screen_pid = re.findall('\d*\.', commands.getoutput('/usr/bin/screen -ls |grep %s' % screen_name))
    if screen_pid:
        commands.getoutput('kill %s' % screen_pid[0][:-1])


def create_screen(screen_name):
    """
    Create screen on local machine

    :param screen_name:
    :return: output if any
    """

    if isinstance(screen_name, str):
        out = commands.getoutput('/usr/bin/screen -dmS %s' % screen_name)
    else:
        out = "No screen name provided"

    return out


def create_screen_windows(screen_name, window_list):
    """

    Create numerous named screen consoles in screen with name screen_name

    :param screen_name:
    :param window_list:
    :return: False, if assert failed or command output
    """

    try:
        assert hasattr(window_list, '__iter__')
        assert len(window_list) > 0
    except AssertionError:
        return False

    for line in window_list:
        out = commands.getoutput("/usr/bin/screen -S %s -X screen -t %s" % (screen_name, line))

    return out


def run_command_in_screen(screen_name, window_name, command):
    """
    :param screen_name:
    :param window_name:
    :param command: full command with ALL arguments
    :return: command execution output if any
    """

    cmd_line = """/usr/bin/screen -S {sn} -p {wn} -X stuff '{exe}\n' """.format(sn=screen_name, wn=window_name, exe=command)
    print cmd_line
    return commands.getoutput(cmd_line)


def test_screens():
    screen_name = "WTF"
    window_list = ["1", "2", "3"]
    create_screen(screen_name)
    create_screen_windows(screen_name, window_list)
    run_command_in_screen(screen_name, "1", "ls -la")
    run_command_in_screen(screen_name, "2", "netstat -tunapl")
    run_command_in_screen(screen_name, "3", "htop")