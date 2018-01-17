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


def get_now_seconds_local():
    return long((datetime.now() - datetime(1970, 1, 1)).total_seconds())


def get_now_seconds_utc():
    return long((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())


def get_now_seconds_utc_ms():
    """
        For a long discussion what is optimal way check this:
            https://stackoverflow.com/questions/38319606/how-to-get-millisecond-and-microsecond-resolution-timestamps-in-python
            https://stackoverflow.com/questions/5998245/get-current-time-in-milliseconds-in-python/21858377#21858377
    """
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)


def sleep_for(num_of_seconds):
    time.sleep(num_of_seconds)


def get_date_time_from_epoch(ts_epoch):
    return datetime.fromtimestamp(1.0 * long(ts_epoch))


def ts_to_string(timest_second_epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timest_second_epoch))


def parse_time(time_string, regex_string):
    utc_time = datetime.strptime(time_string, regex_string)
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return long(epoch_time)
