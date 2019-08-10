import os

from utils.file_utils import log_to_file
from utils.debug_utils import print_to_console, LOG_ALL_ERRORS, FATAL_ERROR_LOG_FILE_NAME


def die_hard(msg):
    log_to_file(msg, FATAL_ERROR_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)
    os._exit(1)
