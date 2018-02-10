from dao.db import init_pg_connection, load_to_postgres
from dao.history_utils import get_history_speedup
from dao.ohlc_utils import get_ohlc_speedup
from data.Candle import CANDLE_TYPE_NAME
from data.OrderHistory import TRADE_HISTORY_TYPE_NAME
from data_access.classes.ConnectionPool import ConnectionPool
from debug_utils import should_print_debug, print_to_console, LOG_ALL_ERRORS
from utils.file_utils import log_to_file
from utils.time_utils import get_now_seconds_utc, sleep_for

# time to poll - 15 minutes
POLL_PERIOD_SECONDS = 900

if __name__ == "__main__":

    pg_conn = init_pg_connection(_db_host="orders.cervsj06c8zw.us-west-1.rds.amazonaws.com", _db_port=5432, _db_name="crypto")

    processor = ConnectionPool()

    while True:
        end_time = get_now_seconds_utc()
        start_time = end_time - POLL_PERIOD_SECONDS

        candles = get_ohlc_speedup(start_time, end_time, processor)

        bad_candles = [x for x in candles if x.timest == 0]
        candles = [x for x in candles if x.timest > 0]

        trade_history = get_history_speedup(start_time, end_time, processor)

        trade_history = [x for x in trade_history if x.timest > start_time]

        load_to_postgres(candles, CANDLE_TYPE_NAME, pg_conn)
        load_to_postgres(trade_history, TRADE_HISTORY_TYPE_NAME, pg_conn)

        if should_print_debug():
            msg = """History retrieval at {tt}:
            Candle size - {num}
            Trade history size - {num2}""".format(tt=end_time, num=len(candles), num2=len(trade_history))
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "candles_trade_history.log")

        for b in bad_candles:
            log_to_file(b, "bad_candles.log")

        print_to_console("Before sleep...", LOG_ALL_ERRORS)
        sleep_for(POLL_PERIOD_SECONDS)
