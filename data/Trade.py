from Deal import Deal

from enums.deal_type import get_deal_type_by_id

from utils.currency_utils import get_currency_name_by_id
from kraken.currency_utils import get_currency_pair_from_kraken

from utils.exchange_utils import get_exchange_name_by_id

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from utils.string_utils import float_to_str


class Trade(Deal):
    def __init__(self, trade_type, exchange_id, pair_id, price, volume, order_book_time, create_time, execute_time=None, deal_id=None):
        self.trade_type = trade_type
        self.exchange_id = exchange_id
        self.pair_id = pair_id
        self.price = price
        self.volume = volume
        self.order_book_time = order_book_time
        self.create_time = create_time
        self.execute_time = execute_time
        self.deal_id = deal_id

    def __str__(self):
        str_repr = "Trade at Exchange: {exch} type: {deal_type} pair: {pair} for volume {vol} with price {price} " \
                   "order_book_time {ob_time} create_time {ct_time} execute_time {ex_time} deal_id {deal_id}".format(
            exch=get_exchange_name_by_id(self.exchange_id),
            deal_type=get_deal_type_by_id(self.trade_type),
            pair=get_currency_name_by_id(self.pair_id),
            vol=float_to_str(self.volume),
            price=float_to_str(self.price),
            ob_time=self.order_book_time,
            ct_time=self.create_time,
            ex_time=self.execute_time,
            deal_id=self.deal_id)

        return str_repr

    def set_deal_id(self, deal_id):
        self.deal_id = deal_id

    @classmethod
    def from_kraken(cls, trade_id, json_doc):
        """
        "OMO3YX-5HSZM-26CQ36": {
 				"status": "open",
 				"fee": "0.000000",
 				"expiretm": 0,
 				"descr": {
 					"leverage": "none",
 					"ordertype": "limit",
 					"price": "0.003310",
 					"pair": "REPXBT",
 					"price2": "0",
 					"type": "sell",
 					"order": "sell 349.78000000 REPXBT @ limit 0.003310"
 				},
 				"vol": "349.78000000",
 				"cost": "0.000000",
 				"misc": "",
 				"price": "0.000000",
 				"starttm": 0,
 				"userref": null,
 				"vol_exec": "0.00000000",
 				"oflags": "fciq",
 				"refid": null,
 				"opentm": 1509591188.429
 			}
        """

        price = float(json_doc["descr"]["price"])
        volume = float(json_doc["vol"])

        create_time = long(json_doc["opentm"])
        order_book_time = create_time # Because at this stage we do not really know it

        trade_type_str = json_doc["descr"]["type"]

        trade_type = DEAL_TYPE.BUY
        if "sell" in trade_type_str:
            trade_type = DEAL_TYPE.SELL

        pair_name = json_doc["descr"]["pair"]

        try:
            pair_id = get_currency_pair_from_kraken(pair_name)

            return Trade(trade_type, EXCHANGE.KRAKEN, pair_id, price, volume, order_book_time, create_time,
                         execute_time=create_time, deal_id=trade_id)
        except Exception, e:
            print "NON supported currency?", pair_name, str(e)

        return None
