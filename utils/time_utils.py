from datetime import datetime
import time


def convert_to_epoch_time(some_string):
    utc_time = datetime.strptime(some_string, "%Y-%m-%d")
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return long(epoch_time)


def convert_to_epoch_midnight(some_string):
    utc_time = datetime.strptime(some_string, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_midnight = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return long(seconds_since_midnight)


def get_now_seconds():
    return long((datetime.now() - datetime(1970, 1, 1)).total_seconds())


def sleep_for(num_of_seconds):
    time.sleep(num_of_seconds)


def get_date_time_from_epoch(ts_epoch):
    return datetime.fromtimestamp(1.0 * long(ts_epoch))
