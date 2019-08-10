import ConfigParser

from data.base_data import BaseData

from utils.debug_utils import LOG_ALL_DEBUG, LOGS_FOLDER, get_debug_level_name_by_id, get_logging_level_id_by_name
from constants import API_KEY_PATH, CACHE_HOST, CACHE_PORT, DB_HOST, DB_NAME, DB_PORT
from enums.exchange import EXCHANGE
from utils.exchange_utils import parse_exchange_ids


class CommonSettings(BaseData):
    def __init__(self,
                 logging_level_id=LOG_ALL_DEBUG,
                 log_folder=LOGS_FOLDER,
                 key_path=API_KEY_PATH,
                 cache_host=CACHE_HOST,
                 cache_port=CACHE_PORT,
                 db_host=DB_HOST,
                 db_port=DB_PORT,
                 db_name=DB_NAME,
                 exchanges_ids=None):

        #           Logging

        self.logging_level_id = logging_level_id
        self.logging_level_name = get_debug_level_name_by_id(self.logging_level_id)
        self.log_folder = log_folder

        #           Keys

        self.key_path = key_path

        #           Cache - Redis so far

        self.cache_host = cache_host
        self.cache_port = cache_port

        #           Postgres
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name

        #           Exchanges
        if not exchanges_ids:
            self.exchanges = EXCHANGE.values()
        else:
            self.exchanges = exchanges_ids

    @classmethod
    def from_cfg(cls, file_name):
        config = ConfigParser.RawConfigParser()
        config.read(file_name)

        log_level_name = config.get("logging", "log_level")
        log_level_id = get_logging_level_id_by_name(log_level_name)

        exchanges_ids = parse_exchange_ids(config.get("common", "exchanges"))

        return CommonSettings(log_level_id,
                              config.get("logging", "logs_folder"),
                              config.get("keys", "path_to_api_keys"),
                              config.get("redis", "redis_host"),
                              config.get("redis", "redis_port"),
                              config.get("postgres", "db_host"),
                              config.get("postgres", "db_port"),
                              config.get("postgres", "db_name"),
                              exchanges_ids)
