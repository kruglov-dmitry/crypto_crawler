import argparse

from data_access.message_queue import QUEUE_TOPICS, get_message_queue, get_notification_id_by_topic_name
from data_access.telegram_notifications import send_single_message

from enums.status import STATUS

from debug_utils import print_to_console, LOG_ALL_ERRORS, set_log_folder, set_logging_level
from utils.file_utils import log_to_file
from utils.time_utils import sleep_for

from deploy.classes.common_settings import CommonSettings


def forward_new_messages(args):
    settings = CommonSettings.from_cfg(args.cfg)

    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)
    msg_queue = get_message_queue(host=settings.cache_host, port=settings.cache_port)

    do_we_have_data = False

    while True:
        for topic_id in QUEUE_TOPICS:
            msg = msg_queue.get_message_nowait(topic_id)
            if msg is not None:
                do_we_have_data = True
                notification_id = get_notification_id_by_topic_name(topic_id)
                err_code = send_single_message(msg, notification_id)
                if err_code == STATUS.FAILURE:
                    err_msg = """telegram_notifier can't send message to telegram. Message will be re-processed on next iteration.
                        {msg}""".format(msg=msg)
                    log_to_file(err_msg, "telegram_notifier.log")
                    print_to_console(err_msg, LOG_ALL_ERRORS)
                    msg_queue.add_message_to_start(topic_id, msg)
                    sleep_for(1)

        #
        #   NOTE: it still can lead to throttling by telegram
        #

        if not do_we_have_data:
            sleep_for(1)

        do_we_have_data = False


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
      Telegram notifier service - every second check message queue for new messages and sent them via bot interface.""")

    parser.add_argument('--cfg', action='store', required=True)

    arguments = parser.parse_args()

    forward_new_messages(arguments)
