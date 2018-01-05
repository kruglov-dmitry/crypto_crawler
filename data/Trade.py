from Deal import Deal

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from enums.deal_type import get_deal_type_by_id

from debug_utils import print_to_console, LOG_ALL_ERRORS
from utils.string_utils import float_to_str
from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_currency_name_by_id
from utils.file_utils import log_to_file
from utils.time_utils import parse_time

from kraken.currency_utils import get_currency_pair_from_kraken
from binance.currency_utils import get_currency_pair_from_binance
from bittrex.currency_utils import get_currency_pair_from_bittrex
from poloniex.currency_utils import get_currency_pair_from_poloniex


class Trade(Deal):
    def __init__(self, trade_type, exchange_id, pair_id, price, volume,
                 order_book_time, create_time, execute_time=None,
                 deal_id=None, executed_volume=None):
        self.trade_type = int(trade_type)
        self.exchange_id = int(exchange_id)
        self.pair_id = int(pair_id)
        self.price = float(price)
        self.volume = float(volume)
        self.order_book_time = long(order_book_time)
        self.create_time = long(create_time)
        self.execute_time = long(execute_time) if execute_time is not None else execute_time
        self.deal_id = deal_id
        self.executed_volume = float(executed_volume) if executed_volume is not None else executed_volume

    def __str__(self):
        str_repr = """
        Trade at Exchange: {exch}
        Type: {deal_type}
        Pair: {pair} for volume {vol} with price {price}
        order_book_time {ob_time} create_time {ct_time} execute_time {ex_time}
        deal_id {deal_id} executed_volume {ex_volume}""".format(
            exch=get_exchange_name_by_id(self.exchange_id),
            deal_type=get_deal_type_by_id(self.trade_type),
            pair=get_currency_name_by_id(self.pair_id),
            vol=float_to_str(self.volume),
            price=float_to_str(self.price),
            ob_time=self.order_book_time,
            ct_time=self.create_time,
            ex_time=self.execute_time,
            deal_id=self.deal_id,
            ex_volume=self.executed_volume
        )

        return str_repr

    def __cmp__(self, other):
        return self.__eq__(other)

    def __eq__(self, other):
        # NOTE: we actually don't care about timest related crap as it will not be the same :(
        # return self.__dict__ == other.__dict__
        return self.trade_type == other.trade_type and self.exchange_id == other.exchange_id and \
            self.pair_id == other.pair_id and self.price == other.price and \
                        self.volume == other.volume and self.deal_id == other.deal_id

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
        price = json_doc["descr"]["price"]
        volume = json_doc["vol"]
        executed_volume = json_doc["vol_exec"]

        create_time = json_doc["opentm"]
        order_book_time = create_time # Because at this stage we do not really know it

        trade_type_str = json_doc["descr"]["type"]

        trade_type = DEAL_TYPE.BUY
        if "sell" in trade_type_str:
            trade_type = DEAL_TYPE.SELL

        pair_name = json_doc["descr"]["pair"]

        pair_id = get_currency_pair_from_kraken(pair_name)
        if pair_id is None:
            msg = "Trade.from_kraken - unsupported pair_name - {n}".format(n=pair_name)
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "error.log")
            return None

        return Trade(trade_type, EXCHANGE.KRAKEN, pair_id, price, volume, order_book_time, create_time,
                         execute_time=create_time, deal_id=trade_id, executed_volume=executed_volume)

    @classmethod
    def from_binance(cls, json_document):
        """
        {u'orderId': 3542537,
        u'clientOrderId': u'L0LbifBNp65Gy2BWTNOOYR',
        u'origQty': u'50.00000000',
        u'icebergQty': u'0.00000000',
        u'symbol': u'XMRBTC',
        u'side': u'SELL',
        u'timeInForce': u'GTC',
        u'status': u'NEW',
        u'stopPrice': u'0.01981500',
        u'time': 1514321524235,
        u'isWorking': False,
        u'type': u'STOP_LOSS_LIMIT',
        u'price': u'0.01975600',
        u'executedQty': u'0.00000000'}
        """
        pair_id = get_currency_pair_from_binance(json_document["symbol"])
        if pair_id is None:
            msg = "Trade.from_binance - unsupported pair_name - {n}".format(n=json_document["symbol"])
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "error.log")
            return None

        timest = json_document["time"]
        price = json_document["price"]
        volume = json_document["origQty"]
        trade_type = DEAL_TYPE.BUY
        if "SELL" in json_document["side"]:
            trade_type = DEAL_TYPE.SELL
        trade_id = json_document["orderId"]
        executed_volume = json_document["executedQty"]

        return Trade(trade_type, EXCHANGE.BINANCE, pair_id, price, volume, timest, timest,
                         execute_time=timest, deal_id=trade_id, executed_volume=executed_volume)

    @classmethod
    def from_bittrex(cls, json_document):
        """
        {u'OrderUuid': u'262a63f5-b901-4efb-b0fb-b6f2f6d203ea',
        u'QuantityRemaining': 8500.0,
        u'IsConditional': False,
        u'ImmediateOrCancel': False,
        u'Uuid': None,
        u'Exchange': u'BTC-GRS',
        u'OrderType': u'LIMIT_BUY',
        u'Price': 0.0,
        u'CommissionPaid': 0.0,
        u'Opened': u'2017-12-26T20:22:41.07',
        u'Limit': 8.969e-05,
        u'Closed': None,
        u'ConditionTarget': None,
        u'CancelInitiated': False,
        u'PricePerUnit': None,
        u'Condition': u'NONE',
        u'Quantity': 8500.0}
        """
        pair_id = get_currency_pair_from_bittrex(json_document["Exchange"])
        if pair_id is None:
            msg = "Trade.from_bittrex - unsupported pair_name - {n}".format(n=json_document["Exchange"])
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "error.log")
            return None

        timest = parse_time(json_document["Opened"], '%Y-%m-%dT%H:%M:%S.%f')

        price = json_document["Limit"]
        volume = json_document["Quantity"]
        trade_type = DEAL_TYPE.BUY
        if "SELL" in json_document["OrderType"]:
            trade_type = DEAL_TYPE.SELL
        trade_id = json_document["OrderUuid"]
        executed_volume = json_document["QuantityRemaining"]

        return Trade(trade_type, EXCHANGE.BINANCE, pair_id, price, volume, timest, timest,
                         execute_time=timest, deal_id=trade_id, executed_volume=executed_volume)

    @classmethod
    def from_poloniex(cls, json_document, pair_name):
        """
        {u'orderNumber': u'22641967545',
        u'margin': 0,
        u'amount': u'10000.00000000',
        u'rate': u'0.00014568',
        u'date': u'2017-12-27 20:29:56',
        u'total': u'1.45680000',
        u'type': u'sell',
        u'startingAmount': u'10000.00000000'}
        """
        pair_id = get_currency_pair_from_poloniex(pair_name)
        if pair_id is None:
            msg = "Trade.from_poloiniex - unsupported pair_name - {n}".format(n=pair_name)
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "error.log")
            return None

        timest = parse_time(json_document["date"], '%Y-%m-%d %H:%M:%S')
        price = json_document["rate"]
        volume = float(json_document["startingAmount"])

        trade_type = DEAL_TYPE.BUY
        if "sell" in json_document["type"]:
            trade_type = DEAL_TYPE.SELL

        trade_id = json_document["orderNumber"]
        executed_volume = volume - float(json_document["amount"])
        return Trade(trade_type, EXCHANGE.POLONIEX, pair_id, price, volume, timest, timest,
                         execute_time=timest, deal_id=trade_id, executed_volume=executed_volume)
