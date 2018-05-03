from currency_utils import get_currency_pair_to_huobi
from utils.currency_utils import split_currency_pairs
from utils.string_utils import truncate_float
from enums.currency import CURRENCY

PRECISION_BTC_NUMBER = {
    "ethbtc":  4,
    "ltcbtc":  4,
    "neobtc":  4,
    "gasbtc":  4,
    "bccbtc":  4,
    "mcobtc":  4,
    "qtumbtc": 4,
    "omgbtc":  4,
    "zrxbtc":  2,
    "zilbtc":  2,
    "kncbtc":  0,
    "linkbtc": 2,
    "saltbtc": 4,
    "iotabtc": 0,
    "mtlbtc":   4,
    "eosbtc":   2,
    "sntbtc":   0,
    "etcbtc":   4,
    "engbtc":   2,
    "astbtc":   0,
    "dashbtc":  4,
    "btgbtc":   4,
    "evxbtc":   2,
    "reqbtc":   1,
    "hsrbtc":   4,
    "trxbtc":   2,
    "powrbtc":  0,
    "xrpbtc":   0,
    "storjbtc": 2,
    "venbtc":   2,
    "rcnbtc":   0,
    "rdnbtc":   0,
    "batbtc":   0,
    "zecbtc":   4,
    "qspbtc":   0,
    "btsbtc":   2,
    "lskbtc":   4,
    "tntbtc":   0,
    "manabtc":  0,
    "bcdbtc":   4,
    "dgdbtc":   4,
    "adxbtc":   2,
    "adabtc":   2,
    "cmtbtc":   2,
    "tnbbtc":   0,
    "icxbtc":   4,
    "ostbtc":   2,
    "elfbtc":   0,
    "xembtc":   2,
    "steembtc": 2,
    "ontbtc":   4,
    "elabtc":   2,
    "iostbtc":  2,
    "wprbtc":   2,
    "lunbtc":   4,
    "itcbtc":   0,
    "qashbtc":  4,
    "blzbtc":   2,
    "appcbtc":  2,
    "rpxbtc":   2,
    "cvcbtc":   0,
    "gntbtc":   2
}


PRECISION_ETH_NUMBER = {
    "qtumeth": 4,
    "eoseth": 2,
    "mcoeth": 4,
    "omgeth": 4,
    "zrxeth": 2,
    "zileth":  2,
    "knceth": 2,
    "linketh": 2,
    "salteth": 4,
    "iotaeth": 0,
    "engeth": 4,
    "asteth": 2,
    "reqeth": 1,
    "hsreth": 4,
    "trxeth": 2,
    "powreth": 0,
    "veneth": 2,
    "rcneth": 0,
    "rdneth": 0,
    "bateth": 0,
    "qspeth": 0,
    "btseth": 2,
    "lsketh": 4,
    "tnteth": 0,
    "manaeth": 0,
    "dgdeth": 4,
    "adxeth": 2,
    "adaeth": 4,
    "cmteth": 2,
    "tnbeth": 0,
    "icxeth": 4,
    "osteth": 2,
    "elfeth": 0,
    "luneth": 4,
    "appceth": 4,
    "iosteth": 2,
    "steemeth": 4,
    "blzeth": 2,
    "onteth": 4,
    "elaeth": 2,
    "naseth": 4,
    "wpreth": 2,
    "qasheth": 4,
    "itceth": 0,
    "cvceth": 1,
    "gnteth": 2,
    "gaseth": 4
}


PRECISION_USDT_NUMBER = {
    "btcusdt": 4,
    "ethusdt": 4,
    "bccusdt": 4,
    "neousdt": 4,
    "ltcusdt": 4,
    "etcusdt": 4,
    "eosusdt": 4,
    "xrpusdt": 2,
    "omgusdt": 4,
    "dashusdt": 4,
    "zecusdt": 4,
    "adausdt": 4,
    "ontusdt": 4,
    "qtumusdt": 4,
    "elausdt": 4,
    "venusdt": 4,
    "zilusdt": 4,
    "xemusdt": 4,
    "nasusdt": 4
}


PRECISION_NUMBER = {
    CURRENCY.BITCOIN: PRECISION_BTC_NUMBER,
    CURRENCY.ETH: PRECISION_ETH_NUMBER,
    CURRENCY.USDT: PRECISION_USDT_NUMBER
}


def round_volume_by_huobi_rules(volume, pair_id):
    pair_name = get_currency_pair_to_huobi(pair_id)
    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if pair_name in PRECISION_NUMBER[base_currency_id]:
        return truncate_float(volume, PRECISION_NUMBER[base_currency_id][pair_name])

    return volume
