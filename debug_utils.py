DEBUG_ENABLED = True

LOG_ALL_ERRORS = 5
LOG_ALL_MARKET_RELATED_CRAP = 10
LOG_ALL_MARKET_NETWORK_RELATED_CRAP = 100
LOG_ALL_DEBUG = 200
LOG_ALL_OTHER_STUFF = 1000
LOG_ALL_TRACE = 10000

DEBUG_LEVEL = LOG_ALL_OTHER_STUFF


DEBUG_LOG_FILE_NAME = "debug.log"
ERROR_LOG_FILE_NAME = "error.log"
POST_RESPONCE_FILE_NAME = "responce.log"
EXPIRED_ORDER_PROCESSING_FILE_NAME = "expire_deal.log"
FAILED_ORDER_PROCESSING_FILE_NAME = "failed_orders.log"
CAP_ADJUSTMENT_TRACE_LOG_FILE_NAME = "cap_price_adjustment.log"


def set_logging_level(effective_debug_level):
    global DEBUG_LEVEL
    DEBUG_LEVEL = effective_debug_level


def set_logging_level_by_name(debug_level_name):
    if debug_level_name is not None:
        effective_debug_level = get_logging_level_id_by_name(debug_level_name)
        set_logging_level(effective_debug_level)


def get_logging_level():
    global DEBUG_LEVEL
    return DEBUG_LEVEL


def should_print_debug():
    global DEBUG_ENABLED
    return DEBUG_ENABLED


def print_to_console(msg, debug_level):
    if get_logging_level() >= debug_level:
        print msg


def get_debug_level_name_by_id(logging_level_id):
    return {
        LOG_ALL_ERRORS: "LOG_ALL_ERRORS",
        LOG_ALL_MARKET_RELATED_CRAP: "LOG_ALL_MARKET_RELATED_CRAP",
        LOG_ALL_MARKET_NETWORK_RELATED_CRAP: "LOG_ALL_MARKET_NETWORK_RELATED_CRAP",
        LOG_ALL_DEBUG: "LOG_ALL_DEBUG",
        LOG_ALL_OTHER_STUFF: "LOG_ALL_OTHER_STUFF"
    }[logging_level_id]


def get_logging_level_id_by_name(logging_level_name):
    return {
        "LOG_ALL_ERRORS": LOG_ALL_ERRORS,
        "LOG_ALL_MARKET_RELATED_CRAP": LOG_ALL_MARKET_RELATED_CRAP,
        "LOG_ALL_MARKET_NETWORK_RELATED_CRAP": LOG_ALL_MARKET_NETWORK_RELATED_CRAP,
        "LOG_ALL_DEBUG": LOG_ALL_DEBUG,
        "LOG_ALL_OTHER_STUFF": LOG_ALL_OTHER_STUFF
    }[logging_level_name.upper()]


LOGS_FOLDER = "./logs/"


def get_log_folder():
    global LOGS_FOLDER
    return LOGS_FOLDER


def set_log_folder(log_folder):
    if log_folder is not None:
        global LOGS_FOLDER
        LOGS_FOLDER = log_folder