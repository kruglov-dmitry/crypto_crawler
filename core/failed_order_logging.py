from utils.file_utils import log_to_file
from debug_utils import FAILED_ORDER_PROCESSING_FILE_NAME


def log_trace_all_closed_orders(open_orders_at_both_exchanges):
    log_to_file("Closed orders below:", FAILED_ORDER_PROCESSING_FILE_NAME)
    for v in open_orders_at_both_exchanges:
        log_to_file(v, FAILED_ORDER_PROCESSING_FILE_NAME)


def log_trace_found_failed_order_in_open(order):
    msg = "Found order {o} among OPEN orders".format(o=order)
    log_to_file(msg, FAILED_ORDER_PROCESSING_FILE_NAME)


def log_trace_found_failed_order_in_history(order):
    msg = "Found order {o} among HISTORY trades".format(o=order)
    log_to_file(msg, FAILED_ORDER_PROCESSING_FILE_NAME)