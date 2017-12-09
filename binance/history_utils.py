from constants import BINANCE_GET_HISTORY
from data.OrderHistory import OrderHistory
from debug_utils import should_print_debug
from data_access.internet import send_request
from enums.status import STATUS


def get_history_binance_url(currency, date_start, date_end):
    # https://api.binance.com/api/v1/aggTrades?symbol=XMRETH
    # Optional startTime, endTime
    final_url = BINANCE_GET_HISTORY + currency

    if should_print_debug():
        print final_url

    return final_url


def get_history_binance(currency, prev_time, now_time):
    all_history_records = []

    final_url = get_history_binance_url(currency, prev_time, now_time)

    err_msg = "get_history_binance called for {pair} at {timest}".format(pair=currency, timest=prev_time)
    error_code, r = send_request(final_url, err_msg)

    if error_code == STATUS.SUCCESS and r is not None :
        """
          {
		    "a": 26129,         // Aggregate tradeId
		    "p": "0.01633102",  // Price
		    "q": "4.70443515",  // Quantity
		    "f": 27781,         // First tradeId
		    "l": 27781,         // Last tradeId
		    "T": 1498793709153, // Timestamp
		    "m": true,          // Was the buyer the maker?
		    "M": true           // Was the trade the best price match?
		  }
        """
        for record in r:
            all_history_records.append(OrderHistory.from_binance(record, currency, now_time))

    return all_history_records
