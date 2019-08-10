import os
import csv

from utils.time_utils import get_now_seconds_utc

from utils.debug_utils import get_log_folder


def save_list_to_file(some_data, file_name):
    with open(file_name, "a") as myfile:
        for entry in some_data:
            myfile.write("%s\n" % str(entry))


def log_to_file(data, file_name, log_dir=None):
    if log_dir is None:
        log_dir = get_log_folder()
    full_path = os.path.join(log_dir, file_name)
    with open(full_path, 'a') as the_file:
        ts = get_now_seconds_utc()
        pid = os.getpid()
        the_file.write("{ts}: PID: {pid} {data}\n".format(ts=ts, pid=pid, data=str(data)))


def save_to_csv_file(file_name, fields_list, array_list):

    with open(file_name, 'w') as f:
        writer = csv.writer(f, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fields_list)
        for entry in array_list:
            writer.writerow(list(entry))

