from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

from utils.file_utils import log_to_file
from utils.debug_utils import SOCKET_ERRORS_LOG_FILE_NAME

SYNC_STAGE = ORDER_BOOK_SYNC_STAGES.UNKNOWN

# Supposedly should be atomic
# src: http://effbot.org/zone/thread-synchronization.htm#atomic-operations


def get_stage():
    return SYNC_STAGE


def set_stage(new_val):
    global SYNC_STAGE
    SYNC_STAGE = new_val
    log_to_file("Changed state to %s" % new_val, SOCKET_ERRORS_LOG_FILE_NAME)
