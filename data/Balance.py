from BaseData import BaseData
from constants import ARBITRAGE_CURRENCY, ZERO_BALANCE
from enums.exchange import EXCHANGE
from enums.currency import CURRENCY

from utils.currency_utils import get_currency_name_by_id
from utils.exchange_utils import get_exchange_name_by_id
from utils.time_utils import ts_to_string
from utils.file_utils import log_to_file
from debug_utils import print_to_console, LOG_ALL_ERRORS

from bittrex.currency_utils import get_currency_name_for_bittrex
from kraken.currency_utils import get_currency_name_for_kraken
from poloniex.currency_utils import get_currency_name_for_poloniex
from binance.currency_utils import get_currency_name_for_binance

"""
time_of_last_update,

    pair_id: volume,
    pair_id: volume,
    ... ,
    pair_id: volume
"""


class Balance(BaseData):
    def __init__(self, exchange_id, last_update, available_balance, total_balance):
        self.exchange_id = exchange_id
        self.last_update = last_update
        self.available_balance = available_balance.copy()
        self.total_balance = total_balance.copy()

    def __str__(self):
        str_repr = "Balance at Exchange: {exch} Last updated: {dt} timest: {ts} %".format(
            exch=get_exchange_name_by_id(self.exchange_id),
            dt=ts_to_string(self.last_update),
            ts=self.last_update)

        str_repr += " Available balance:"
        for currency_id in self.available_balance:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.available_balance[currency_id])

        str_repr += " Total balance:"
        for currency_id in self.total_balance:
            str_repr += " " + get_currency_name_by_id(currency_id) + " - " + str(self.total_balance[currency_id])

        return str_repr

    def do_we_have_enough_bitcoin(self, threahold):
        if CURRENCY.BITCOIN in self.available_balance:
            return self.available_balance[CURRENCY.BITCOIN] > threahold

        print "do_we_have_enough_bitcoin: no bitcoin within Balance 0_o"
        return False

    def get_bitcoin_balance(self):
        return self.available_balance.get(CURRENCY.BITCOIN)

    @classmethod
    def from_poloniex(cls, last_update, json_document):

        total_balance = {}
        available_balance = {}

        """
         {"LTC":{"available":"5.015","onOrders":"1.0025","btcValue":"0.078"},"NXT:{...} ... }

         FIXME NOTE: those bastards always return ALL coins not very efficient
        """

        for currency_id in ARBITRAGE_CURRENCY:

            available_balance[currency_id] = ZERO_BALANCE

            currency_name = get_currency_name_for_poloniex(currency_id)
            if currency_name in json_document:
                volume = float(json_document[currency_name]["available"])
                available_balance[currency_id] = volume

                locked_volume = float(json_document[currency_name]["onOrders"])
                total_balance[currency_id] = locked_volume + volume

        return Balance(EXCHANGE.POLONIEX, last_update, available_balance, total_balance)

    @classmethod
    def from_kraken(cls, last_update, json_document):

        # FIXME re-review
        initial_balance = {}

        """
        {u'DASH': u'33.2402410500', u'BCH': u'22.4980093900', ... }
        """

        for currency_id in ARBITRAGE_CURRENCY:

            initial_balance[currency_id] = ZERO_BALANCE

            try:
                currency_name = get_currency_name_for_kraken(currency_id)
                if currency_name in json_document:
                    volume = float(json_document[currency_name])
                    initial_balance[currency_id] = volume
            except Exception, e:
                error_msg = "Can't find currency_id - {id}".format(id=currency_id)
                msg = "Balance.from_kraken Exception: {excp} {msg}".format(excp=error_msg, msg=str(e))
                print_to_console(msg, LOG_ALL_ERRORS)
                log_to_file(msg, "error.txt")

        return Balance(EXCHANGE.KRAKEN, last_update, initial_balance, initial_balance)

    @classmethod
    def from_bittrex(cls, last_update, json_document):

        total_balance = {}
        available_balance = {}

        """
        [{u'Available': 21300.0, u'Currency': u'ARDR', u'Balance': 21300.0, u'Pending': 0.0,
        u'CryptoAddress': u'76730d86115b49b9b7f71578feb35b7da1ca6c13e5f745aa9b630707f5439e68'},

        {u'Available': 49704.04069438, u'Currency': u'BAT', u'Balance': 49704.04069438, u'Pending': 0.0,
        u'CryptoAddress': None},
        """

        for currency_id in ARBITRAGE_CURRENCY:

            total_balance[currency_id] = ZERO_BALANCE
            available_balance[currency_id] = ZERO_BALANCE

            currency_name = get_currency_name_for_bittrex(currency_id)

            for entry in json_document:
                if currency_name == entry["Currency"]:
                    volume = float(entry["Balance"])
                    total_balance[currency_id] = volume
                    volume = float(entry["Available"])
                    available_balance[currency_id] = volume

        return Balance(EXCHANGE.BITTREX, last_update, available_balance, total_balance)

    @classmethod
    def from_binance(cls, last_update, json_document):

        total_balance = {}
        available_balance = {}

        """
            "makerCommission": 15,
            "takerCommission": 15,
            "buyerCommission": 0,
            "sellerCommission": 0,
            "canTrade": true,
            "canWithdraw": true,
            "canDeposit": true,
            "balances": [
                {
                    "asset": "BTC",
                    "free": "4723846.89208129",
                    "locked": "0.00000000"
                },
                
        """
        for currency_id in ARBITRAGE_CURRENCY:

            available_balance[currency_id] = ZERO_BALANCE

            currency_name = get_currency_name_for_binance(currency_id)

            for entry in json_document["balances"]:
                if currency_name == entry["asset"]:
                    volume = float(entry["free"])
                    available_balance[currency_id] = volume
                    locked_volume = float(entry["locked"])
                    total_balance[currency_id] = locked_volume + volume

        return Balance(EXCHANGE.BINANCE, last_update, available_balance, total_balance)
