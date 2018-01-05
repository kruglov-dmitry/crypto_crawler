from data_access.classes.MessageQueue import QUEUE_TOPICS, get_message_queue, get_notification_id_by_topic_name
from data_access.telegram_notifications import send_single_message
from debug_utils import print_to_console, LOG_ALL_ERRORS
from enums.status import STATUS
from utils.file_utils import log_to_file
from utils.time_utils import sleep_for

if __name__ == "__main__":

    msg_queue = get_message_queue()
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

        if not do_we_have_data:
            sleep_for(1)

        do_we_have_data = False
