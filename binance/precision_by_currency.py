from binance.currency_utils import get_currency_pair_to_binance
from utils.currency_utils import split_currency_pairs
from utils.string_utils import truncate_float
from enums.currency import CURRENCY


# BASE_CURRENCY = BTC
PRECISION_BTC_NUMBER = {
    "ETHBTC":  3,
    "LTCBTC":  2,
    "BNBBTC":  0,
    "NEOBTC":  2,
    "GASBTC":  2,
    "BCCBTC":  3,
    "MCOBTC":  2,
    "WTCBTC":  0,
    "QTUMBTC": 2,
    "OMGBTC":  2,
    "ZRXBTC":  0,
    "ZILBTC":  0,
    "STRATBTC": 2,
    "SNGLSBTC": 0,
    "BQXBTC":  0,
    "KNCBTC":  0,
    "FUNBTC":  0,
    "SNMBTC":  0,
    "LINKBTC": 0,
    "XVGBTC":  0,
    "CTRBTC":  0,
    "SALTBTC": 2,
    "IOTABTC": 0,
    "MDABTC":  0,
    "MTLBTC":   0,
    "SUBBTC":   0,
    "EOSBTC":   0,
    "SNTBTC":   0,
    "ETCBTC":   2,
    "MTHBTC":   0,
    "ENGBTC":   0,
    "DNTBTC":   0,
    "BNTBTC":   0,
    "ASTBTC":   0,
    "DASHBTC":  3,
    "ICNBTC":   0,
    "OAXBTC":   0,
    "BTGBTC":   2,
    "EVXBTC":   0,
    "REQBTC":   0,
    "LRCBTC":   0,
    "VIBBTC":   0,
    "HSRBTC":   0,
    "TRXBTC":   0,
    "POWRBTC":  0,
    "ARKBTC":   2,
    "YOYOBTC":  0,
    "XRPBTC":   0,
    "MODBTC":   0,
    "ENJBTC":   0,
    "STORJBTC": 0,
    "VENBTC":   0,
    "KMDBTC":   0,
    "RCNBTC":   0,
    "NULSBTC":  0,
    "RDNBTC":   0,
    "XMRBTC":   3,
    "DLTBTC":   3,
    "AMBBTC":   3,
    "BATBTC":   0,
    "ZECBTC":   3,
    "BCPTBTC":  0,
    "ARNBTC":   0,
    "GVTBTC":   2,
    "CDTBTC":   0,
    "GXSBTC":   2,
    "POEBTC":   0,
    "QSPBTC":   0,
    "BTSBTC":   0,
    "XZCBTC":   2,
    "LSKBTC":   2,
    "TNTBTC":   0,
    "FUELBTC":  0,
    "MANABTC":  0,
    "BCDBTC":   3,
    "DGDBTC":   3,
    "ADXBTC":   0,
    "ADABTC":   0,
    "PPTBTC":   2,
    "CMTBTC":   0,
    "XLMBTC":   0,
    "CNDBTC":   0,
    "LENDBTC":  0,
    "WABIBTC":  0,
    "TNBBTC":   0,
    "WAVESBTC": 2,
    "ICXBTC":   2,
    "GTOBTC":   0,
    "OSTBTC":   0,
    "ELFBTC":   0,
    "AIONBTC":  0,
    "NEBLBTC":  0,
    "XEMBTC": 0
}


PRECISION_ETH_NUMBER = {
    "BNBETH": 0,
    "QTUMETH": 2,
    "SNTETH": 0,
    "BNTETH": 2,
    "EOSETH": 2,
    "OAXETH": 0,
    "DNTETH": 0,
    "MCOETH": 2,
    "ICNETH": 0,
    "WTCETH": 2,
    "OMGETH": 2,
    "ZRXETH": 0,
    "ZILETH":  0,
    "STRATETH": 2,
    "SNGLSETH": 0,
    "BXQETH": 0,
    "KNCETH": 0,
    "FUNETH": 0,
    "SNMETH": 0,
    "NEOETH": 2,
    "LINKETH": 1,
    "XVGETH": 1,
    "CTRETH": 1,
    "SALTETH": 2,
    "IOTAETH": 0,
    "MDAETH": 0,
    "MTLETH": 0,
    "SUBETH": 1,
    "ETCETH": 2,
    "MTHETH": 0,
    "ENGETH": 0,
    "ASTETH": 0,
    "DASHETH": 3,
    "BTGETH": 2,
    "EVXETH": 0,
    "REQETH": 0,
    "LRCETH": 0,
    "VIBETH": 0,
    "HSRETH": 2,
    "TRXETH": 0,
    "POWRETH": 0,
    "ARKETH": 2,
    "YOYOETH": 0,
    "XRPETH": 0,
    "MODETH": 0,
    "ENJETH": 0,
    "STORJETH": 0,
    "VENETH": 0,
    "KMDETH": 0,
    "RCNETH": 0,
    "NULSETH": 0,
    "RDNETH": 0,
    "XMRETH": 0,
    "DLTETH": 0,
    "AMBETH": 0,
    "BCCETH": 0,
    "BATETH": 0,
    "ZECETH": 3,
    "BCPTETH": 0,
    "ARNETH": 0,
    "GVTETH": 2,
    "CDTETH": 0,
    "GXSETH": 2,
    "POEETH": 0,
    "QSPETH": 0,
    "BTSETH": 0,
    "XZCETH": 0,
    "LSKETH": 0,
    "TNTETH": 0,
    "FUELETH": 0,
    "MANAETH": 0,
    "BCDETH": 3,
    "DGDETH": 3,
    "ADXETH": 0,
    "ADAETH": 0,
    "PPTETH": 0,
    "CMTETH": 0,
    "XLMETH": 0,
    "CNDETH": 0,
    "LENDETH": 0,
    "WABIETH": 0,
    "LTCETH": 3,
    "TNBETH": 0,
    "WAVESETH": 2,
    "ICXETH": 2,
    "GTOETH": 0,
    "OSTETH": 0,
    "ELFETH": 0,
    "AIONETH": 2,
    "NEBLETH": 2,
    "BRDETH": 0,
    "EDOETH": 2,
    "WINGSETH": 0,
    "NAVETH": 2,
    "LUNETH": 2,
    "TRIGETH": 2,
    "APPCETH": 0,
    "VIBEETH": 0,
    "RLCETH": 2,
    "INSETH": 2,
    "PIVXETH": 2,
    "IOSTETH": 0,
    "CHATETH": 0,
    "STEEMETH": 2,
    "NANOETH": 2,
    "VIAETH": 2,
    "BLZETH": 0,
    "AEETH": 2,
    "RPXETH": 0,
    "NCASHETH": 0,
    "POAETH": 0,
    "XEMETH": 0
}


PRECISION_USDT_NUMBER = {
    "BTCUSDT": 6,
    "ETHUSDT": 5,
    "BNBUSDT": 2,
    "BCCUSDT": 5,
    "NEOUSDT": 3,
    "LTCUSDT": 5
}

PRECISION_NUMBER = {
    CURRENCY.BITCOIN: PRECISION_BTC_NUMBER,
    CURRENCY.ETH: PRECISION_ETH_NUMBER,
    CURRENCY.USDT: PRECISION_USDT_NUMBER
}


def round_volume_by_binance_rules(volume, pair_id):
    pair_name = get_currency_pair_to_binance(pair_id)
    base_currency_id, dst_currency_id = split_currency_pairs(pair_id)

    if pair_name in PRECISION_NUMBER[base_currency_id]:
        return truncate_float(volume, PRECISION_NUMBER[base_currency_id][pair_name])

    return volume
