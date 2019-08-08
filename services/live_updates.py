import os
import threading

from utils.time_utils import get_now_seconds_utc, ts_to_string_utc
from utils.exchange_utils import get_exchange_name_by_id

BIDS_HEADLINE = "BIDS\t\t\t\t\t\t\t\t\tBIDS"
ASKS_HEADLINE = "ASKS\t\t\t\t\t\t\t\t\tASKS"

ORDER_BOOK_DELIMITER = '\t\t\t'


def _print_top10(exchange_id, order_book_buy, order_book_sell):
    header = "Number of threads: {tn} Last update {ts} {td} from {up_exch_name}\n" \
             "\n{buy_exchange}\t\t\t\t\t\t\t\t\t{sell_exchange}\n".\
        format(tn=threading.active_count(), ts=get_now_seconds_utc(),
               td=ts_to_string_utc(get_now_seconds_utc()),
               up_exch_name=get_exchange_name_by_id(exchange_id),
               buy_exchange=get_exchange_name_by_id(order_book_buy.exchange_id),
               sell_exchange=get_exchange_name_by_id(order_book_sell.exchange_id)
    )
    os.system('clear')

    print(header)

    print(BIDS_HEADLINE)
    lb1 = len(order_book_buy.bid)
    lb2 = len(order_book_sell.bid)
    for idx in xrange(0, 10):
        if idx < lb1:
            print order_book_buy.bid[idx],
        else:
            print None,
        print ORDER_BOOK_DELIMITER,
        if idx < lb2:
            print order_book_sell.bid[idx]
        else:
            print None

    print(ASKS_HEADLINE)
    la1 = len(order_book_buy.ask)
    la2 = len(order_book_sell.ask)
    for idx in xrange(0, 10):
        if idx < la1:
            print order_book_buy.ask[idx],
        else:
            print None
        print ORDER_BOOK_DELIMITER,
        if idx < la2:
            print order_book_sell.ask[idx]
        else:
            print None
