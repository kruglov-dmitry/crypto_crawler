from BaseData import BaseData
from constants import ARBITRAGE_CURRENCY
from enums.exchange import EXCHANGE
from utils.currency_utils import get_currency_name_by_id, get_currency_name_for_kraken, \
    get_currency_name_for_bittrex, get_currency_name_for_poloniex
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import ts_to_string

"""
time_of_last_update,

    pair_id: volume,
    pair_id: volume,
    ... ,
    pair_id: volume
"""


class Balance(BaseData):
    def __init__(self, exchange_id, last_update, initial_balance):
        self.exchange_id = exchange_id
        self.last_update = last_update
        self.balance = initial_balance

    def __str__(self):
        str_repr = "Balance at Exchange: {exch} Last updated: {dt} timest: {ts} %".format(
            exch=get_exchange_name_by_id(self.exchange_id),
            dt=ts_to_string(self.last_update),
            ts=self.last_update)

        str_repr += " Balance:"
        for currency_id in self.balance:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.balance[currency_id])

        return str_repr

    @classmethod
    def from_poloniex(cls, last_update, json_document):

        initial_balance = {}

        """
         {u'XVC': u'0.00000000', u'SRCC': u'0.00000000', u'EXE': u'0.00000000',

         FIXME NOTE: those bastards always return ALL coins not very efficient
        """

        for currency_id in ARBITRAGE_CURRENCY:
            currency_name = get_currency_name_for_poloniex(currency_id)
            if currency_name in json_document:
                volume = json_document[currency_name]
                initial_balance[currency_id] = volume

        return Balance(EXCHANGE.POLONIEX, last_update, initial_balance)

    @classmethod
    def from_kraken(cls, last_update, json_document):

        initial_balance = {}

        """
        {u'DASH': u'33.2402410500', u'BCH': u'22.4980093900', ... }
        """

        for currency_id in ARBITRAGE_CURRENCY:
            currency_name = get_currency_name_for_kraken(currency_id)
            if currency_name in json_document:
                volume = json_document[currency_name]
                initial_balance[currency_id] = volume

        return Balance(EXCHANGE.KRAKEN, last_update, initial_balance)

    @classmethod
    def from_bittrex(cls, last_update, json_document):

        initial_balance = {}

        """
        [{u'Available': 21300.0, u'Currency': u'ARDR', u'Balance': 21300.0, u'Pending': 0.0,
        u'CryptoAddress': u'76730d86115b49b9b7f71578feb35b7da1ca6c13e5f745aa9b630707f5439e68'},

        {u'Available': 49704.04069438, u'Currency': u'BAT', u'Balance': 49704.04069438, u'Pending': 0.0,
        u'CryptoAddress': None},
        """

        for currency_id in ARBITRAGE_CURRENCY:
            currency_name = get_currency_name_for_bittrex(currency_id)

            for entry in json_document:
                if currency_name == entry["Currency"]:
                    volume = entry["Balance"]
                    initial_balance[currency_id] = volume

        return Balance(EXCHANGE.BITTREX, last_update, initial_balance)
