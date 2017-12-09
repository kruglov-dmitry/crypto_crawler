from enums.currency import CURRENCY
from enums.currency_pair import CURRENCY_PAIR


def get_currency_id_from_binance(currency_name):
    return {
        'BTC': CURRENCY.BITCOIN,
        'DASH': CURRENCY.DASH,
        'BCC': CURRENCY.BCC,
        'XRP': CURRENCY.XRP,
        'LTC': CURRENCY.LTC,
        'ETC': CURRENCY.ETC,
        'ETH': CURRENCY.ETH,
        'SC': CURRENCY.SC,
        'DGB': CURRENCY.DGB,
        'XEM': CURRENCY.XEM,
        'ARDR': CURRENCY.ARDR,
        'OMG': CURRENCY.OMG,
        'ZEC': CURRENCY.ZEC,
        'REP': CURRENCY.REP,
        'XMR': CURRENCY.XMR,
        'DOGE': CURRENCY.DOGE,
        'DCR': CURRENCY.DCR,
        'USDT': CURRENCY.USDT
    }.get(currency_name)


def get_currency_name_for_binance(currency_id):
    return {
        CURRENCY.BITCOIN: 'BTC',
        CURRENCY.DASH: 'DASH',
        CURRENCY.BCC: 'BCC',
        CURRENCY.XRP: 'XRP',
        CURRENCY.LTC: 'LTC',
        CURRENCY.ETC: 'ETC',
        CURRENCY.ETH: 'ETH',
        CURRENCY.SC: 'SC',
        CURRENCY.DGB: 'DGB',
        CURRENCY.XEM: 'XEM',
        CURRENCY.ARDR: 'ARDR',
        CURRENCY.OMG: 'OMG',
        CURRENCY.ZEC: 'ZEC',
        CURRENCY.REP: 'REP',
        CURRENCY.XMR: 'XMR',
        CURRENCY.DOGE: 'DOGE',
        CURRENCY.DCR: 'DCR',
        CURRENCY.USDT: 'USDT'
    }.get(currency_id)


def get_currency_pair_from_binance(pair_id):
    return {
        'DASHBTC': CURRENCY_PAIR.BTC_TO_DASH,
        'ETHBTC': CURRENCY_PAIR.BTC_TO_ETH,
        'LTCBTC': CURRENCY_PAIR.BTC_TO_LTC,
        'XRPBTC': CURRENCY_PAIR.BTC_TO_XRP,
        'BCCBTC': CURRENCY_PAIR.BTC_TO_BCC,
        'ETCBTC': CURRENCY_PAIR.BTC_TO_ETC,
        'OMGBTC': CURRENCY_PAIR.BTC_TO_OMG,
        'ZECBTC': CURRENCY_PAIR.BTC_TO_ZEC,
        'XMRBTC': CURRENCY_PAIR.BTC_TO_XMR,
        'DASHETH': CURRENCY_PAIR.ETH_TO_DASH,
        'XRPETH': CURRENCY_PAIR.ETH_TO_XRP,
        'BCCETH': CURRENCY_PAIR.ETH_TO_BCC,
        'ETCETH': CURRENCY_PAIR.ETH_TO_ETC,
        'OMGETH': CURRENCY_PAIR.ETH_TO_OMG,
        'ZECETH': CURRENCY_PAIR.ETH_TO_ZEC,
        'XMRETH': CURRENCY_PAIR.ETH_TO_XMR,
        'BTCUSDT': CURRENCY_PAIR.USDT_TO_BTC,
        'BCCUSDT': CURRENCY_PAIR.USDT_TO_BCC,
        'ETHUSDT': CURRENCY_PAIR.USDT_TO_ETH,
    }.get(pair_id)


def get_currency_pair_to_binance(pair_id):
    return {
        CURRENCY_PAIR.BTC_TO_DASH: 'DASHBTC',
        CURRENCY_PAIR.BTC_TO_ETH: 'ETHBTC',
        CURRENCY_PAIR.BTC_TO_LTC: 'LTCBTC',
        CURRENCY_PAIR.BTC_TO_XRP: 'XRPBTC',
        CURRENCY_PAIR.BTC_TO_BCC: 'BCCBTC',
        CURRENCY_PAIR.BTC_TO_ETC: 'ETCBTC',
        CURRENCY_PAIR.BTC_TO_OMG: 'OMGBTC',
        CURRENCY_PAIR.BTC_TO_ZEC: 'ZECBTC',
        CURRENCY_PAIR.BTC_TO_XMR: 'XMRBTC',
        CURRENCY_PAIR.ETH_TO_DASH: 'DASHETH',
        CURRENCY_PAIR.ETH_TO_XRP: 'XRPETH',
        CURRENCY_PAIR.ETH_TO_BCC: 'BCCETH',
        CURRENCY_PAIR.ETH_TO_ETC: 'ETCETH',
        CURRENCY_PAIR.ETH_TO_OMG: 'OMGETH',
        CURRENCY_PAIR.ETH_TO_ZEC: 'ZECETH',
        CURRENCY_PAIR.ETH_TO_XMR: 'XMRETH',
        CURRENCY_PAIR.USDT_TO_BTC: 'BTCUSDT',
        CURRENCY_PAIR.USDT_TO_BCC: 'BCCUSDT',
        CURRENCY_PAIR.USDT_TO_ETH: 'ETHUSDT',
    }.get(pair_id)
