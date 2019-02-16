from enums.sync_stages import ORDER_BOOK_SYNC_STAGES

stage = ORDER_BOOK_SYNC_STAGES.UNKNOWN

# Supposedly should be atomic
# src: http://effbot.org/zone/thread-synchronization.htm#atomic-operations


def get_stage():
    return stage


def set_stage(new_val):
    global stage
    stage = new_val