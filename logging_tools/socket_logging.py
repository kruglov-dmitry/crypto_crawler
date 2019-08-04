from debug_utils import LOG_ALL_ERRORS, print_to_console, SOCKET_ERRORS_LOG_FILE_NAME

from utils.file_utils import log_to_file


def log_conect_to_websocket(exch_name):
    msg = "{exch_name} - before main loop".format(exch_name=exch_name)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_error_on_receive_from_socket(exch_name, e):
    msg = "{exch_name} - triggered exception during reading from socket = {e}. Reseting stage!".format(
        exch_name=exch_name, e=str(e))
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_heartbeat_is_missing(exch_name, timeout, last_heartbeat_ts, ts_now):
    msg = "{exch_name} - Havent heard from exchange more than {timeout}. Last update - {l_update} but " \
          "now - {n_time}. Reseting stage!".format(exch_name=exch_name,
                                                   timeout=timeout,
                                                   l_update=last_heartbeat_ts,
                                                   n_time=ts_now)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_subscription_cancelled(exch_name):
    msg = "{exch_name} - exit from main loop. Current thread will be finished.".format(exch_name=exch_name)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_websocket_disconnect(exch_name, e):
    msg = "{exch_name} - triggered exception during closing socket = {e} at disconnect!".format(
        exch_name=exch_name, e=str(e))
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_send_heart_beat_failed(exch_name, e):
    msg = "{exch_name}: connection terminated with error: {er}".format(exch_name=exch_name, er=str(e))
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_sequence_id_mismatch(exch_name, prev_sequence_id, new_sequence_id):
    msg = "{exch_name} - sequence_id mismatch! Prev: {prev} New: {new}".format(
        exch_name=exch_name, prev=prev_sequence_id, new=new_sequence_id)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_subscribe_to_exchange_heartbeat(exch_name):
    msg = "{exch_name} - subscribing to exchange heartbeat".format(exch_name=exch_name)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)


def log_unsubscribe_to_exchange_heartbeat(exch_name):
    msg = "{exch_name} - DISCONNECT FROM exchange heartbeat".format(exch_name=exch_name)
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)
    print_to_console(msg, LOG_ALL_ERRORS)
