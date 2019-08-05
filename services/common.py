from dao.db import init_pg_connection
from deploy.classes.common_settings import CommonSettings
from debug_utils import set_logging_level, set_log_folder


def process_args(args):
    settings = CommonSettings.from_cfg(args.cfg)
    pg_conn = init_pg_connection(_db_host=settings.db_host,
                                 _db_port=settings.db_port,
                                 _db_name=settings.db_name)

    set_log_folder(settings.log_folder)
    set_logging_level(settings.logging_level_id)

    return pg_conn, settings
