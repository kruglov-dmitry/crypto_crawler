import os
import threading

from utils.file_utils import log_to_file
from utils.debug_utils import print_to_console, LOG_ALL_ERRORS, FATAL_ERROR_LOG_FILE_NAME


def die_hard(msg):
    log_to_file(msg, FATAL_ERROR_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)
    os._exit(1)


def start_process_daemon(method, args):
    new_thread = threading.Thread(target=method, args=args)
    new_thread.daemon = True
    new_thread.start()
    return new_thread


def clear_queue(m_queue):
    while True:
        try:
            entry = m_queue.get(block=False)
        except:
            entry = None

        if entry is None:
            break

        m_queue.task_done()
