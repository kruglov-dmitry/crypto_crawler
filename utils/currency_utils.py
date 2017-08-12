from enums.currency_pair import CURRENCY_PAIR


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
        'ETCXBT': CURRENCY_PAIR.BTC_TO_ETC
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


def get_pair_name_by_id(pair_id):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: "BTC_TO_DASH",
        CURRENCY_PAIR.BTC_TO_ETH: "BTC_TO_ETH",
        CURRENCY_PAIR.BTC_TO_LTC: "BTC_TO_LTC",
        CURRENCY_PAIR.BTC_TO_XRP: "BTC_TO_XRP",
        CURRENCY_PAIR.BTC_TO_BCC: "BTC_TO_BCC",
        CURRENCY_PAIR.BTC_TO_ETC: "BTC_TO_ETC",
        CURRENCY_PAIR.BTC_TO_SC: 'BTC_TO_SC',
        CURRENCY_PAIR.BTC_TO_DGB: 'BTC_DGB',
        CURRENCY_PAIR.BTC_TO_XEM: 'BTC_XEM',
        CURRENCY_PAIR.BTC_TO_ARDR: 'BTC_ARDR'
    }[pair_id]