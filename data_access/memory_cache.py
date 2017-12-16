import redis as _redis
from constants import CACHE_HOST, CACHE_PORT
from dao.balance_utils import get_balance_by_exchange
from enums.status import STATUS
from utils.exchange_utils import get_exchange_name_by_id
import pickle
from utils.file_utils import log_to_file


class MemoryCache:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def get_counter(self):
        return self.r.incr('nonce')

    def _init_nonce(self):
        pass

    def update_balance_by_exchange(self, exchange_id):
        status_code, balance = get_balance_by_exchange(exchange_id)
        exchange_name = get_exchange_name_by_id(exchange_id)
        if status_code == STATUS.SUCCESS:
            self.r.set(exchange_name, pickle.dumps(balance))
            return balance
        else:
            msg = "Can't update balance for exchange_id = {exch1} {exch_name}".format(exch1=exchange_id,
                                                                                            exch_name=exchange_name)
            log_to_file(msg, "cache.log")

        return None

    def get_balance(self, exchange_id):
        exchange_name = get_exchange_name_by_id(exchange_id)
        balance = pickle.loads(self.r.get(exchange_name))
        if balance is None :
            balance = self.update_balance_by_exchange(exchange_id)
            if balance is None:
                print "ERROR: BALANCE IS STILL NONE!!! for", exchange_name

        return balance

    def init_balances(self, exchanges_ids):
        for exchange_id in exchanges_ids:
            self.update_balance_by_exchange(exchange_id)

# FIXME NOTE temporary workaround for in-memory caching

local_cache = MemoryCache(host=CACHE_HOST, port=CACHE_PORT)