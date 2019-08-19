from enums.exchange import EXCHANGE
from enums.currency import CURRENCY

from utils.time_utils import get_now_seconds_local, sleep_for

from core.backtest import dummy_order_state_init

from kraken.market_utils import cancel_order_kraken
from kraken.order_utils import get_orders_kraken
from kraken.balance_utils import get_balance_kraken


def test_kraken_placing_deals(krak_key):
    order_state = dummy_order_state_init()
    # order_state = get_updated_order_state(order_state)

    for x in order_state[EXCHANGE.KRAKEN].open_orders:
        if x.pair_id == CURRENCY.BCC and x.volume == 0.1 and x.price == 0.5:
            cancel_order_kraken(krak_key, x.deal_id)

    # order_state = get_updated_order_state(order_state)
    cnt = 0
    for x in order_state[EXCHANGE.KRAKEN].open_orders:
        if x.pair_id == CURRENCY.BCC and x.volume == 0.1 and x.price == 0.5:
            cnt += 1
            print x

    print cnt

    print order_state[EXCHANGE.KRAKEN]
    ts1 = get_now_seconds_local()
    for x in range(10000):
        # add_sell_order_kraken_till_the_end(krak_key, "BCHXBT", price=0.5, amount=0.1, order_state=order_state[EXCHANGE.KRAKEN])
        sleep_for(30)

    ts2 = get_now_seconds_local()
    # order_state = get_updated_order_state(order_state)
    print "Goal was to set 10000 deals: "
    print "Total number of open orders: ", len(order_state[EXCHANGE.KRAKEN].open_orders)
    print "It take ", ts2-ts1, " seconds"


def test_kraken_market_utils(krak_key):
    res = get_orders_kraken(krak_key)

    print res.get_total_num_of_orders()

    print res

    error_code, r = get_balance_kraken(krak_key)
    print r
    """add_buy_order_kraken_try_till_the_end(krak_key, "XETHXXBT", 0.07220, 0.02)
    add_sell_order_kraken_till_the_end(krak_key, "XETHXXBT", 0.07220, 0.02)
    add_sell_order_kraken_till_the_end(krak_key, "XETHXXBT", 0.07220, 0.02)
    """
    cancel_order_kraken(krak_key, 'O6PGMG-DXKYV-UU4MNM')
