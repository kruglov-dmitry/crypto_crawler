from dao.db import init_pg_connection
from deploy.classes.common_settings import CommonSettings
from utils.debug_utils import set_logging_level, set_log_folder

from data_access.memory_cache import get_cache
from data_access.priority_queue import get_priority_queue
from data_access.message_queue import get_message_queue


def process_args(args):
    settings = CommonSettings.from_cfg(args.cfg)
    pg_conn = init_pg_connection(_db_host=settings.db_host,
                                 _db_port=settings.db_port,
                                 _db_name=settings.db_name)

    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    return pg_conn, settings


def init_queues(app_settings):
    priority_queue = get_priority_queue(host=app_settings.cache_host, port=app_settings.cache_port)
    msg_queue = get_message_queue(host=app_settings.cache_host, port=app_settings.cache_port)
    local_cache = get_cache(host=app_settings.cache_host, port=app_settings.cache_port)

    return priority_queue, msg_queue, local_cache
