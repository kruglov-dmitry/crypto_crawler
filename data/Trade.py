from Deal import Deal

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from enums.deal_type import get_order_type_by_id

from debug_utils import get_logging_level, LOG_ALL_DEBUG, print_to_console, LOG_ALL_ERRORS, ERROR_LOG_FILE_NAME
from utils.string_utils import float_to_str
from utils.exchange_utils import get_exchange_name_by_id
from utils.currency_utils import get_pair_name_by_id
from utils.file_utils import log_to_file
from utils.time_utils import parse_time, ts_to_string_local

from kraken.currency_utils import get_currency_pair_from_kraken
from binance.currency_utils import get_currency_pair_from_binance
from bittrex.currency_utils import get_currency_pair_from_bittrex
from poloniex.currency_utils import get_currency_pair_from_poloniex
from huobi.currency_utils import get_currency_pair_from_huobi


class Trade(Deal):
    def __init__(self, trade_type, exchange_id, pair_id, price, volume,
                 order_book_time, create_time, execute_time=None,
                 order_id=None, trade_id=None, executed_volume=None, arbitrage_id=-13):
        self.trade_type = int(trade_type)
        self.exchange_id = int(exchange_id)
        self.pair_id = int(pair_id)
        self.price = float(price)
        self.volume = float(volume)
        self.order_book_time = long(order_book_time)
        self.create_time = long(create_time)
        self.execute_time = long(execute_time) if execute_time is not None else execute_time
        self.order_id = order_id
        self.trade_id = trade_id
        self.executed_volume = float(executed_volume) if executed_volume is not None else executed_volume
        self.arbitrage_id = long(arbitrage_id)

    def __str__(self):
        str_repr = """
        Trade at Exchange: {exch}
        Type: {deal_type}
        Pair: {pair} for volume {vol} with price {price}
        order_book_time {ob_time} create_time {ct_time} execute_time {ex_time}
        Executed at: {dt}
        order_id {order_id} trade_id {trade_id} executed_volume {ex_volume}
        arbitrage_id {a_id}
        """.format(
            exch=get_exchange_name_by_id(self.exchange_id),
            deal_type=get_order_type_by_id(self.trade_type),
            pair=get_pair_name_by_id(self.pair_id),
            vol=float_to_str(self.volume),
            price=float_to_str(self.price),
            ob_time=self.order_book_time,
            ct_time=self.create_time,
            ex_time=self.execute_time,
            dt=ts_to_string_local(self.execute_time),
            order_id=self.order_id,
            trade_id=self.trade_id,
            ex_volume=self.executed_volume,
            a_id=self.arbitrage_id
        )

        return str_repr

    def __cmp__(self, other):
        return self.__eq__(other)

    def __eq__(self, other):
        if get_logging_level() >= LOG_ALL_DEBUG:
            msg = "compare {u} with {b}".format(u=self,b=other)
            log_to_file(msg,"expire_deal.log")
        if other is None:
            return False
        # NOTE: we actually don't care about timest related crap as it will not be the same :(
        # return self.__dict__ == other.__dict__
        return self.order_id == other.order_id and self.trade_type == other.trade_type and \
               self.exchange_id == other.exchange_id and self.pair_id == other.pair_id

    def set_order_id(self, order_id):
        self.order_id = order_id

    @classmethod
    def get_fields(cls):
        # for class object you can use dir()
        return ["arbitrage_id", "exchange_id", "pair_id", "trade_type", "price", "volume", "order_book_time",
                "create_time", "execute_time", "execute_datetime", "order_id", "executed_volume"]

    def __iter__(self):
        return iter([self.arbitrage_id, get_exchange_name_by_id(self.exchange_id), get_pair_name_by_id(self.pair_id),
                     get_order_type_by_id(self.trade_type), self.price, self.volume, self.order_book_time,
                     self.create_time, self.execute_time, ts_to_string_local(self.execute_time),
                     self.order_id, self.trade_id, self.executed_volume])

    @classmethod
    def from_kraken(cls, order_id, json_doc):
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
            log_to_file(msg, ERROR_LOG_FILE_NAME)
            return None

        return Trade(trade_type, EXCHANGE.KRAKEN, pair_id, price, volume, order_book_time, create_time,
                     execute_time=create_time, order_id=order_id, trade_id=order_id, executed_volume=executed_volume)

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

        timest = 0.001 * long(json_document["time"])
        price = json_document["price"]
        volume = json_document["origQty"]
        trade_type = DEAL_TYPE.BUY
        if "SELL" in json_document["side"]:
            trade_type = DEAL_TYPE.SELL
        order_id = json_document["orderId"]
        executed_volume = json_document["executedQty"]

        return Trade(trade_type, EXCHANGE.BINANCE, pair_id, price, volume, timest, timest, execute_time=timest,
                     order_id=order_id, trade_id=order_id, executed_volume=executed_volume)

    @classmethod
    def from_binance_history(cls, json_document, pair_name):
        """
            u'orderId': 7632926,
            u'isBuyer': False,
            u'price': u'0.00933400',
            u'isMaker': False,
            u'qty': u'14.95000000',
            u'commission': u'0.00013954',
            u'time': 1520011967196,
            u'commissionAsset': u'ETH',
            u'id': 346792,
            u'isBestMatch': True

        :param json_document:
        :return:
        """
        pair_id = get_currency_pair_from_binance(pair_name)
        if pair_id is None:
            msg = "Trade.from_binance - unsupported pair_name - {n}".format(n=json_document["symbol"])
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "error.log")
            return None

        timest = 0.001 * long(json_document["time"])
        price = json_document["price"]
        volume = json_document["qty"]

        trade_type = DEAL_TYPE.BUY
        if not json_document["isBuyer"]:
            trade_type = DEAL_TYPE.SELL
        order_id = json_document["orderId"]     # Effective 01.03.2018
        trade_id = json_document["id"]
        executed_volume = volume

        return Trade(trade_type, EXCHANGE.BINANCE, pair_id, price, volume, timest, timest, execute_time=timest,
                     order_id=order_id, trade_id=trade_id, executed_volume=executed_volume)

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

        try:
            timest = parse_time(json_document["Opened"], '%Y-%m-%dT%H:%M:%S.%f')
        except:
            timest = parse_time(json_document["Opened"], '%Y-%m-%dT%H:%M:%S')

        price = json_document["Limit"]
        volume = float(json_document["Quantity"])
        trade_type = DEAL_TYPE.BUY
        if "SELL" in json_document["OrderType"]:
            trade_type = DEAL_TYPE.SELL
        trade_id = json_document["OrderUuid"]
        executed_volume = volume - float(json_document["QuantityRemaining"])

        return Trade(trade_type, EXCHANGE.BITTREX, pair_id, price, volume, timest, timest, execute_time=timest,
                     order_id=trade_id, executed_volume=executed_volume)

    @classmethod
    def from_bittrex_history(cls, json_document):
        """
        {
           u'OrderUuid':u'b9f52a13-571f-4560-91af-a52f0c0c3f1f',
           u'QuantityRemaining':0.0,
           u'ImmediateOrCancel':False,
           u'IsConditional':False,
           u'Exchange':u'BTC-STRAT',
           u'TimeStamp':   u'2018-02-07T19:50:03.01   ', u'   Price':0.00440505,
           u'ConditionTarget':None,
           u'Commission':1.101e-05,
           u'Limit':0.00088101,
           u'Closed':   u'2018-02-08T13:25:55.133   ', u'   OrderType':u'LIMIT_SELL',
           u'PricePerUnit':0.00088101,
           u'Condition':u'NONE',
           u'Quantity':5.0
        }

        :param json_document:
        :return:
        """
        order_id = json_document["OrderUuid"]
        pair_id = get_currency_pair_from_bittrex(json_document["Exchange"])
        if pair_id is None:
            msg = "Trade.from_bittrex - unsupported pair_name - {n}".format(n=json_document["Exchange"])
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, "error.log")
            return None

        try:
            timest = parse_time(json_document["TimeStamp"], '%Y-%m-%dT%H:%M:%S.%f')
        except:
            timest = parse_time(json_document["TimeStamp"], '%Y-%m-%dT%H:%M:%S')

        try:
            execute_timest = parse_time(json_document["Closed"], '%Y-%m-%dT%H:%M:%S.%f')
        except:
            execute_timest = parse_time(json_document["Closed"], '%Y-%m-%dT%H:%M:%S')

        trade_type = DEAL_TYPE.BUY
        if "SELL" in json_document["OrderType"]:
            trade_type = DEAL_TYPE.SELL

        price = json_document["PricePerUnit"]

        volume = float(json_document["Quantity"])
        executed_volume = volume - float(json_document["QuantityRemaining"])

        return Trade(trade_type, EXCHANGE.BITTREX, pair_id, price, volume, order_book_time=timest, create_time=timest,
                     execute_time=execute_timest, order_id=order_id, trade_id=order_id, executed_volume=executed_volume)


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
            msg = "Trade.from_poloniex - unsupported pair_name - {n}".format(n=pair_name)
            print_to_console(msg, LOG_ALL_ERRORS)
            log_to_file(msg, ERROR_LOG_FILE_NAME)
            return None

        timest = parse_time(json_document["date"], '%Y-%m-%d %H:%M:%S')
        price = json_document["rate"]
        volume = float(json_document["startingAmount"])

        trade_type = DEAL_TYPE.BUY
        if "sell" in json_document["type"]:
            trade_type = DEAL_TYPE.SELL

        order_id = json_document["orderNumber"]
        executed_volume = volume - float(json_document["amount"])
        return Trade(trade_type, EXCHANGE.POLONIEX, pair_id, price, volume, timest, timest, execute_time=timest,
                     order_id=order_id, trade_id=order_id, executed_volume=executed_volume)

    @classmethod
    def from_poloniex_history(cls, json_document, pair_name):
        """
        { "globalTradeID": 25129732,
        "tradeID": "6325758",
        "date": "2016-04-05 08:08:40",
         "rate": "0.02565498",
         "amount": "0.10000000",
         "total": "0.00256549",
         "fee": "0.00200000",
         "orderNumber": "34225313575",
         "type": "sell",
         "category": "exchange" }
        :return:
        """
        pair_id = get_currency_pair_from_poloniex(pair_name)
        trade_type = DEAL_TYPE.BUY
        if "sell" in json_document["type"]:
            trade_type = DEAL_TYPE.SELL

        order_id = json_document["orderNumber"]
        trade_id = json_document["tradeID"]
        timest = parse_time(json_document["date"], '%Y-%m-%d %H:%M:%S')
        price = json_document["rate"]
        volume = float(json_document["amount"])

        return Trade(trade_type, EXCHANGE.POLONIEX, pair_id, price, volume, timest, timest, execute_time=timest,
                     order_id=order_id, trade_id=trade_id, executed_volume=volume)

    @classmethod
    def from_huobi(cls, json_document, pair_name):
        """
            06.04.2018 NOTE - no filled amount, have to use special method to retrieve this data

            "id": 59378,
            "symbol": "ethusdt",
            "account-id": 100009,
            "amount": "10.1000000000",
            "price": "100.1000000000",
            "created-at": 1494901162595,
            "type": "buy-limit",
            "field-amount": "10.1000000000",
            "field-cash-amount": "1011.0100000000",
            "field-fees": "0.0202000000",
            "finished-at": 1494901400468,
            "user-id": 1000,
            "source": "api",
            "state": "filled",
            "canceled-at": 0,
            "exchange": "huobi",
            "batch": ""
        :return:
        """

        pair_id = get_currency_pair_from_huobi(pair_name)
        trade_type = DEAL_TYPE.BUY
        if "sell" in json_document["type"]:
            trade_type = DEAL_TYPE.SELL

        order_id = str(json_document["id"])
        trade_id = json_document["id"]

        create_timest = 0.001 * long(json_document["created-at"])
        executed_timest = 0.001 * long(json_document["finished-at"])

        price = json_document["price"]
        volume = float(json_document["amount"])
        executed_volume = float(json_document["field-amount"])

        return Trade(trade_type, EXCHANGE.HUOBI, pair_id, price, volume, create_timest, create_timest, execute_time=executed_timest,
                     order_id=order_id, trade_id=trade_id, executed_volume=executed_volume)

    @classmethod
    def from_row(cls, db_row):
        """
        row order:
        arbitrage_id, exchange_id, trade_type, pair_id, price, volume, executed_volume, order_id, trade_id,
        order_book_time, create_time, execute_time

        2, 4, 2, 11, 0.001554, 2.0, None, '9103224', 151612795
        :param row:
        :return:
        """
        arbitrage_id = db_row[0]
        exchange_id = db_row[1]
        trade_type = db_row[2]
        pair_id = db_row[3]
        price = db_row[4]
        volume = float(db_row[5])
        executed_volume = db_row[6]
        order_id = db_row[7]
        trade_id = db_row[8]
        order_book_time = db_row[9]
        create_time = db_row[10]
        execute_time = db_row[11]

        res = Trade(trade_type, exchange_id, pair_id, price, volume, order_book_time, create_time, execute_time,
                    order_id, trade_id, executed_volume, arbitrage_id)

        return res

    @classmethod
    def from_bittrex_scv(cls, row):
        """
            Export from bittrex history:


            OrderUuid, 8269d382-b7f6-4ac2-9e7f-33ce45887b72,
            Exchange, BTC-XRP,
            Type, LIMIT_BUY,
            Quantity, 478.7867564,
            Limit, 0.00002155,
            CommissionPaid, 0.00002579,
            Price, 0.01031785,
            Opened, 12/4/2017 4:02:43 AM,
            Closed 12/4/2017 4:05:11 AM

        """

        order_id = row[0]
        pair_id = get_currency_pair_from_bittrex(row[1])
        trade_type = DEAL_TYPE.BUY
        if "SELL" in row[2]:
            trade_type = DEAL_TYPE.SELL

        volume = float(row[3])
        price = float(row[5])

        arbitrage_id = -50
        exchange_id = EXCHANGE.BITTREX

        executed_volume = db_row[6]

        trade_id = db_row[8]
        order_book_time = db_row[9]
        create_time = db_row[10]
        execute_time = db_row[11]

        res = Trade(trade_type, exchange_id, pair_id, price, volume, order_book_time, create_time, execute_time,
                    order_id, trade_id, executed_volume, arbitrage_id)

        return res
