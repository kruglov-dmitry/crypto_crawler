from enums.currency_pair import CURRENCY_PAIR
from enums.currency import CURRENCY


def split_currency_pairs(pair_id):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: (CURRENCY.BITCOIN, CURRENCY.DASH),
        CURRENCY_PAIR.BTC_TO_ETH: (CURRENCY.BITCOIN, CURRENCY.ETH),
        CURRENCY_PAIR.BTC_TO_LTC: (CURRENCY.BITCOIN, CURRENCY.LTC),
        CURRENCY_PAIR.BTC_TO_XRP: (CURRENCY.BITCOIN, CURRENCY.XRP),
        CURRENCY_PAIR.BTC_TO_BCC: (CURRENCY.BITCOIN, CURRENCY.BCC),
        CURRENCY_PAIR.BTC_TO_ETC: (CURRENCY.BITCOIN, CURRENCY.ETC),
        CURRENCY_PAIR.BTC_TO_SC: (CURRENCY.BITCOIN, CURRENCY.SC),
        CURRENCY_PAIR.BTC_TO_DGB: (CURRENCY.BITCOIN, CURRENCY.DGB),
        CURRENCY_PAIR.BTC_TO_XEM: (CURRENCY.BITCOIN, CURRENCY.XEM),
        CURRENCY_PAIR.BTC_TO_ARDR: (CURRENCY.BITCOIN, CURRENCY.ARDR)
    }[pair_id]


def get_currency_pair_from_poloniex(currency):
    return {
        'BTC_DASH': CURRENCY_PAIR.BTC_TO_DASH,
        'BTC_ETH': CURRENCY_PAIR.BTC_TO_ETH,
        'BTC_LTC': CURRENCY_PAIR.BTC_TO_LTC,
        'BTC_XRP': CURRENCY_PAIR.BTC_TO_XRP,
        'BTC_ETC': CURRENCY_PAIR.BTC_TO_ETC,
        'BTC_SC': CURRENCY_PAIR.BTC_TO_SC,
        'BTC_DGB' : CURRENCY_PAIR.BTC_TO_DGB,
        'BTC_XEM': CURRENCY_PAIR.BTC_TO_XEM,
        'BTC_ARDR': CURRENCY_PAIR.BTC_TO_ARDR
    }[currency]


def get_currency_pair_from_kraken(currency):
    return {
        'DASHXBT': CURRENCY_PAIR.BTC_TO_DASH,
        'XETHXXBT': CURRENCY_PAIR.BTC_TO_ETH,
        'XLTCXXBT': CURRENCY_PAIR.BTC_TO_LTC,
        'XXRPXXBT': CURRENCY_PAIR.BTC_TO_XRP,
        'BCHXBT': CURRENCY_PAIR.BTC_TO_BCC,
        'XETCXXBT': CURRENCY_PAIR.BTC_TO_ETC
    }[currency]


def get_currency_pair_from_bittrex(currency):
    return {
        'BTC-DASH': CURRENCY_PAIR.BTC_TO_DASH,
        'BTC-ETH': CURRENCY_PAIR.BTC_TO_ETH,
        'BTC-LTC': CURRENCY_PAIR.BTC_TO_LTC,
        'BTC-XRP': CURRENCY_PAIR.BTC_TO_XRP,
        'BTC-BCC': CURRENCY_PAIR.BTC_TO_BCC,
        'BTC-ETC': CURRENCY_PAIR.BTC_TO_ETC,
        'BTC-SC': CURRENCY_PAIR.BTC_TO_SC,
        'BTC-DGB': CURRENCY_PAIR.BTC_TO_DGB,
        'BTC-XEM': CURRENCY_PAIR.BTC_TO_XEM,
        'BTC-ARDR': CURRENCY_PAIR.BTC_TO_ARDR
    }[currency]


def get_currency_pair_to_poloniex(currency):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: 'BTC_DASH',
        CURRENCY_PAIR.BTC_TO_ETH: 'BTC_ETH',
        CURRENCY_PAIR.BTC_TO_LTC: 'BTC_LTC',
        CURRENCY_PAIR.BTC_TO_XRP: 'BTC_XRP',
        CURRENCY_PAIR.BTC_TO_ETC: 'BTC_ETC',
        CURRENCY_PAIR.BTC_TO_SC: 'BTC_SC',
        CURRENCY_PAIR.BTC_TO_DGB : 'BTC_DGB',
        CURRENCY_PAIR.BTC_TO_XEM: 'BTC_XEM',
        CURRENCY_PAIR.BTC_TO_ARDR: 'BTC_ARDR'
    }[currency]


def get_currency_pair_to_kraken(currency):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: 'DASHXBT',
        CURRENCY_PAIR.BTC_TO_ETH: 'XETHXXBT',
        CURRENCY_PAIR.BTC_TO_LTC: 'XLTCXXBT',
        CURRENCY_PAIR.BTC_TO_XRP: 'XXRPXXBT',
        CURRENCY_PAIR.BTC_TO_BCC: 'BCHXBT',
        CURRENCY_PAIR.BTC_TO_ETC: 'XETCXXBT'
    }[currency]


def get_currency_pair_to_bittrex(currency):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: 'BTC-DASH',
        CURRENCY_PAIR.BTC_TO_ETH: 'BTC-ETH',
        CURRENCY_PAIR.BTC_TO_LTC: 'BTC-LTC',
        CURRENCY_PAIR.BTC_TO_XRP: 'BTC-XRP',
        CURRENCY_PAIR.BTC_TO_BCC: 'BTC-BCC',
        CURRENCY_PAIR.BTC_TO_ETC: 'BTC-ETC',
        CURRENCY_PAIR.BTC_TO_SC: 'BTC-SC',
        CURRENCY_PAIR.BTC_TO_DGB: 'BTC-DGB',
        CURRENCY_PAIR.BTC_TO_XEM: 'BTC-XEM',
        CURRENCY_PAIR.BTC_TO_ARDR: 'BTC-ARDR'
    }[currency]


def get_pair_name_by_id(pair_id):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: "BTC_TO_DASH",
        CURRENCY_PAIR.BTC_TO_ETH: "BTC_TO_ETH",
        CURRENCY_PAIR.BTC_TO_LTC: "BTC_TO_LTC",
        CURRENCY_PAIR.BTC_TO_XRP: "BTC_TO_XRP",
        CURRENCY_PAIR.BTC_TO_BCC: "BTC_TO_BCC",
        CURRENCY_PAIR.BTC_TO_ETC: "BTC_TO_ETC",
        CURRENCY_PAIR.BTC_TO_SC: "BTC_TO_SC",
        CURRENCY_PAIR.BTC_TO_DGB: "BTC_TO_DGB",
        CURRENCY_PAIR.BTC_TO_XEM: "BTC_TO_XEM",
        CURRENCY_PAIR.BTC_TO_ARDR: "BTC_TO_ARDR"
    }[pair_id]


"""
    NOTE:   routine below is used only for balance retrieval
            supported currencies are 
            ARBITRAGE_CURRENCY = [CURRENCY.DASH, CURRENCY.BCC, CURRENCY.XRP, CURRENCY.LTC, CURRENCY.ETC, CURRENCY.ETH]
"""


def get_currency_id_from_kraken(currency_name):
    return {
        'DASH': CURRENCY.DASH,
        'BCH': CURRENCY.BCC,
        'XXRP': CURRENCY.XRP,
        'XLTC': CURRENCY.LTC,
        'XETC': CURRENCY.ETC,
        'XETH': CURRENCY.ETH
    }[currency_name]


def get_currency_name_for_kraken(currency_id):
    return {
        CURRENCY.DASH: 'DASH',
        CURRENCY.BCC: 'BCH',
        CURRENCY.XRP: 'XXRP',
        CURRENCY.LTC: 'XLTC',
        CURRENCY.ETC: 'XETC',
        CURRENCY.ETH: 'XETH'
    }[currency_id]


def get_currency_id_from_bittrex(currency_name):
    return {
        'DASH': CURRENCY.DASH,
        'BCC': CURRENCY.BCC,
        'XRP': CURRENCY.XRP,
        'LTC': CURRENCY.LTC,
        'ETC': CURRENCY.ETC,
        'ETH': CURRENCY.ETH
    }[currency_name]


def get_currency_name_for_bittrex(currency_id):
    return {
        CURRENCY.DASH: 'DASH',
        CURRENCY.BCC: 'BCC',
        CURRENCY.XRP: 'XRP',
        CURRENCY.LTC: 'LTC',
        CURRENCY.ETC: 'ETC',
        CURRENCY.ETH: 'ETH'
    }[currency_id]


def get_currency_id_from_poloniex(currency_name):
    return {
        'DASH': CURRENCY.DASH,
        'BCC': CURRENCY.BCC,
        'XRP': CURRENCY.XRP,
        'LTC': CURRENCY.LTC,
        'ETC': CURRENCY.ETC,
        'ETH': CURRENCY.ETH
    }[currency_name]


def get_currency_name_for_poloniex(currency_id):
    return {
        CURRENCY.DASH: 'DASH',
        CURRENCY.BCC: 'BCC',
        CURRENCY.XRP: 'XRP',
        CURRENCY.LTC: 'LTC',
        CURRENCY.ETC: 'ETC',
        CURRENCY.ETH: 'ETH'
    }[currency_id]


def get_currency_name_by_id(currency_id):
    return {
        CURRENCY.DASH: 'DASH',
        CURRENCY.BCC: 'BCC',
        CURRENCY.XRP: 'XRP',
        CURRENCY.LTC: 'LTC',
        CURRENCY.ETC: 'ETC',
        CURRENCY.ETH: 'ETH'
    }[currency_id]