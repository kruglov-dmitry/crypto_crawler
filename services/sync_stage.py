from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

from utils.file_utils import log_to_file
from debug_utils import SOCKET_ERRORS_LOG_FILE_NAME

stage = ORDER_BOOK_SYNC_STAGES.UNKNOWN

# Supposedly should be atomic
# src: http://effbot.org/zone/thread-synchronization.htm#atomic-operations


def get_stage():
    return stage


def set_stage(new_val):
    global stage
    stage = new_val
    log_to_file("Changed state to %s" % new_val, SOCKET_ERRORS_LOG_FILE_NAME)