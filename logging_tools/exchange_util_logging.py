# from utils.file_utils import log_to_file
from debug_utils import print_to_console, LOG_ALL_ERRORS


def log_wrong_exchange_id(exchange_id):
    msg = "UNKNOWN exchange id provided - {idx}".format(idx=exchange_id)
    print_to_console(msg, LOG_ALL_ERRORS)
    # log_to_file(msg, "balance.log")
