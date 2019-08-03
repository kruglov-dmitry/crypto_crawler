class CURRENCY_PAIR(object):
    BTC_TO_DASH = 1
    BTC_TO_ETH = 2
    BTC_TO_LTC = 3
    BTC_TO_XRP = 4
    BTC_TO_BCC = 5
    BTC_TO_ETC = 6
    BTC_TO_SC = 7
    BTC_TO_DGB = 8
    BTC_TO_XEM = 9
    BTC_TO_ARDR = 10
    BTC_TO_OMG = 11
    BTC_TO_ZEC = 12
    BTC_TO_REP = 13
    BTC_TO_XMR = 14
    BTC_TO_DOGE = 15
    BTC_TO_DCR = 16         # NOT EXIST on kraken
    BTC_TO_NEO = 17         # NOT EXIST on kraken, poloniex
    BTC_TO_QTUM = 18        # NOT EXIST on kraken, poloniex
    BTC_TO_EOS = 19         # not exist on bittrex, poloniex
    BTC_TO_IOTA = 20        # not exist on bittrex, kraken, poloniex
    BTC_TO_BTG = 21         # NOT EXIST on kraken, poloniex
    BTC_TO_WTC = 22         # not exist on bittrex, kraken, poloniex
    BTC_TO_KNC = 23         # not exist on bittrex, kraken, poloniex
    BTC_TO_BAT = 24         # NOT EXIST on kraken, poloniex
    BTC_TO_ZRX = 25         # not exist on bittrex, kraken
    BTC_TO_RDN = 26         # not exist on bittrex, kraken, poloniex
    BTC_TO_GAS = 27         # not exist on bittrex, kraken
    BTC_TO_ADA = 28         # not exist on kraken, poloniex
    BTC_TO_RCN = 29         # not exist on kraken, poloniex
    BTC_TO_QSP = 30         # Not exist on bittrex, kraken, poloniex
    BTC_TO_XBY = 31         # Not exist on binance, bittrex, kraken, poloniex
    BTC_TO_PAC = 32         # Not exist on binance, bittrex, kraken, poloniex
    BTC_TO_RDD = 33         # Not exist on binance, kraken, poloniex
    BTC_TO_ICX = 34         # Not exist on bittrex, kraken, poloniex
    BTC_TO_WABI = 35        # Not exist on bittrex, kraken, poloniex
    BTC_TO_XLM = 36         # at poloniex named STR
    BTC_TO_TRX = 37         # Not exist on bittrex, kraken, poloniex
    BTC_TO_AION = 38        # Not exist on bittrex, kraken, poloniex
    BTC_TO_ITC = 39         # Not exist on binance, bittrex, kraken, poloniex
    BTC_TO_ARK = 40
    BTC_TO_STRAT = 41
    BTC_TO_LSK = 42         # LISK Polo/trex/binance
    BTC_TO_ENG = 43         # ENIGMA  trex/binance
    BTC_TO_XVG = 44         # VERGE   trex/binance

    BTC_TO_ONT = 45         # huobi
    BTC_TO_HSR = 46         # huobi
    BTC_TO_ZIL = 47         # huobi
    BTC_TO_VEN = 48         # huobi
    BTC_TO_ELF = 49         # huobi
    BTC_TO_BLZ = 50         # huobi
    BTC_TO_REQ = 51         # huobi
    BTC_TO_LINK = 52        # huobi

    BTC_TO_NAS = 53         # huobi
    BTC_TO_ELA = 54         # huobi

    ETH_TO_DASH = 1001
    ETH_TO_BTC = 1002       # NOT EXIST ON kraken, poloniex, bittrex
    ETH_TO_LTC = 1003
    ETH_TO_XRP = 1004
    ETH_TO_BCC = 1005
    ETH_TO_ETC = 1006
    ETH_TO_SC = 1007
    ETH_TO_DGB = 1008
    ETH_TO_XEM = 1009
    ETH_TO_ARDR = 1010      # NOT EXIST ON kraken, poloniex, bittrex
    ETH_TO_OMG = 1011
    ETH_TO_ZEC = 1012
    ETH_TO_REP = 1013
    ETH_TO_XMR = 1014

    ETH_TO_NEO = 1015       # NOT EXIST on kraken, poloniex
    ETH_TO_QTUM = 1016      # NOT EXIST on kraken, poloniex
    ETH_TO_EOS = 1017       # not exist on bittrex, poloniex
    ETH_TO_IOTA = 1018      # not exist on bittrex, kraken, poloniex
    ETH_TO_BTG = 1019       # NOT EXIST on kraken, poloniex
    ETH_TO_WTC = 1020       # not exist on bittrex, kraken, poloniex
    ETH_TO_KNC = 1021       # not exist on bittrex, kraken, poloniex
    ETH_TO_BAT = 1022       # NOT EXIST on kraken, poloniex
    ETH_TO_ZRX = 1023       # not exist on bittrex, kraken
    ETH_TO_RDN = 1024       # not exist on bittrex, kraken, poloniex
    ETH_TO_GAS = 1025       # Not exist on binance, bittrex, kraken
    ETH_TO_ADA = 1026       # not exist on kraken, poloniex
    ETH_TO_RCN = 1027       # not exist on kraken, poloniex
    ETH_TO_QSP = 1028       # Not exist on bittrex, kraken, poloniex
    ETH_TO_XBY = 1029       # Not exist on binance, bittrex, kraken, poloniex
    ETH_TO_PAC = 1030       # Not exist on binance, bittrex, kraken, poloniex
    ETH_TO_RDD = 1031       # Not exist on binance, bittrex, kraken, poloniex
    ETH_TO_ICX = 1032       # Not exist on bittrex, kraken, poloniex
    ETH_TO_WABI = 1033      # Not exist on bittrex, kraken, poloniex
    ETH_TO_XLM = 1034       # not exist on kraken, poloniex
    ETH_TO_TRX = 1035       # Not exist on bittrex, kraken, poloniex
    ETH_TO_AION = 1036      # Not exist on bittrex, kraken, poloniex
    ETH_TO_ITC = 1037       # Not exist on binance, bittrex, poloniex
    ETH_TO_ARK = 1038       # Not exist at bittrex, poloniex
    ETH_TO_STRAT = 1039     # Not exist at poloniex
    ETH_TO_LSK = 1040       # LISK binance\poloniex\huobi
    ETH_TO_ENG = 1041       # ENIGMA  trex/binance
    ETH_TO_XVG = 1042       # VERGE   trex/binance

    ETH_TO_ONT = 1043       # huobi
    ETH_TO_HSR = 1044       # huobi
    ETH_TO_ZIL = 1045       # huobi
    ETH_TO_VEN = 1046       # huobi
    ETH_TO_ELF = 1047       # huobi
    ETH_TO_BLZ = 1048       # huobi
    ETH_TO_REQ = 1049       # huobi
    ETH_TO_LINK = 1050      # huobi

    ETH_TO_NAS = 1051  # huobi
    ETH_TO_ELA = 1052  # huobi

    USD_TO_DASH = 2001
    USD_TO_ETH = 2002
    USD_TO_LTC = 2003
    USD_TO_XRP = 2004
    USD_TO_BCC = 2005
    USD_TO_ETC = 2006
    USD_TO_SC = 2007        # NOT EXIST ON kraken, poloniex, bittrex
    USD_TO_DGB = 2008       # NOT EXIST ON kraken, poloniex, bittrex
    USD_TO_XEM = 2009
    USD_TO_ARDR = 2010      # NOT EXIST ON kraken, poloniex, bittrex
    # NOTE: NO OMG!
    USD_TO_BTC = 2011
    USD_TO_ZEC = 2012
    USD_TO_REP = 2013
    USD_TO_XMR = 2014

    USDT_TO_DASH = 3001     # NOT EXIST ON kraken
    USDT_TO_ETH = 3002      # NOT EXIST ON kraken
    USDT_TO_LTC = 3003      # NOT EXIST ON kraken
    USDT_TO_XRP = 3004      # NOT EXIST ON kraken
    USDT_TO_BCC = 3005      # NOT EXIST ON kraken
    USDT_TO_ETC = 3006      # NOT EXIST ON kraken
    USDT_TO_SC = 3007        # NOT EXIST ON kraken, poloniex, bittrex
    USDT_TO_DGB = 3008       # NOT EXIST ON kraken, poloniex, bittrex
    USDT_TO_XEM = 3009
    USDT_TO_ARDR = 3010      # NOT EXIST ON kraken, poloniex, bittrex
    USDT_TO_BTC = 3011      # NOT EXIST ON kraken
    USDT_TO_ZEC = 3012      # NOT EXIST ON kraken
    USDT_TO_REP = 3013      # NOT EXIST ON kraken
    USDT_TO_XMR = 3014      # NOT EXIST ON kraken

    USDT_TO_NEO = 3015      # binance
    USDT_TO_QTUM = 3016
    USDT_TO_EOS = 3017
    USDT_TO_IOTA = 3018
    USDT_TO_BTG = 3019
    USDT_TO_WTC = 3020
    USDT_TO_KNC = 3021
    USDT_TO_BAT = 3022
    USDT_TO_ZRX = 3023
    USDT_TO_RDN = 3024
    USDT_TO_GAS = 3025
    USDT_TO_ADA = 3026
    USDT_TO_RCN = 3027
    USDT_TO_QSP = 3028
    USDT_TO_XBY = 3029
    USDT_TO_PAC = 3030
    USDT_TO_RDD = 3031
    USDT_TO_ICX = 3032
    USDT_TO_WABI = 3033
    USDT_TO_XLM = 3034      # suddenly exist at poloniex
    USDT_TO_TRX = 3035
    USDT_TO_AION = 3036
    USDT_TO_ITC = 3037
    USDT_TO_XVG = 3038      # VERGE   trex
    USDT_TO_OMG = 3039      # huobi

    USDT_TO_HSR = 3040      # huobi
    USDT_TO_ZIL = 3041      # huobi
    USDT_TO_VEN = 3042      # huobi
    USDT_TO_ELF = 3043      # huobi

    USDT_TO_NAS = 3044      # huobi
    USDT_TO_ELA = 3045      # huobi

    USD_TO_USDT = 4000      # kraken only

    @classmethod
    def values(cls):
        return [CURRENCY_PAIR.BTC_TO_DASH,
                CURRENCY_PAIR.BTC_TO_ETH,
                CURRENCY_PAIR.BTC_TO_LTC,
                CURRENCY_PAIR.BTC_TO_XRP,
                CURRENCY_PAIR.BTC_TO_BCC,
                CURRENCY_PAIR.BTC_TO_ETC,
                CURRENCY_PAIR.BTC_TO_SC,
                CURRENCY_PAIR.BTC_TO_DGB,
                CURRENCY_PAIR.BTC_TO_XEM,
                CURRENCY_PAIR.BTC_TO_ARDR,
                CURRENCY_PAIR.BTC_TO_OMG,
                CURRENCY_PAIR.BTC_TO_ZEC,
                CURRENCY_PAIR.BTC_TO_REP,
                CURRENCY_PAIR.BTC_TO_XMR,
                CURRENCY_PAIR.BTC_TO_DOGE,
                CURRENCY_PAIR.BTC_TO_DCR,
                CURRENCY_PAIR.BTC_TO_NEO,
                CURRENCY_PAIR.BTC_TO_QTUM,
                CURRENCY_PAIR.BTC_TO_EOS,
                CURRENCY_PAIR.BTC_TO_IOTA,
                CURRENCY_PAIR.BTC_TO_BTG,
                CURRENCY_PAIR.BTC_TO_WTC,
                CURRENCY_PAIR.BTC_TO_KNC,
                CURRENCY_PAIR.BTC_TO_BAT,
                CURRENCY_PAIR.BTC_TO_ZRX,
                CURRENCY_PAIR.BTC_TO_RDN,
                CURRENCY_PAIR.BTC_TO_GAS,
                CURRENCY_PAIR.BTC_TO_ADA,
                CURRENCY_PAIR.BTC_TO_RCN,
                CURRENCY_PAIR.BTC_TO_QSP,
                CURRENCY_PAIR.BTC_TO_XBY,
                CURRENCY_PAIR.BTC_TO_PAC,
                CURRENCY_PAIR.BTC_TO_RDD,
                CURRENCY_PAIR.BTC_TO_ICX,
                CURRENCY_PAIR.BTC_TO_WABI,
                CURRENCY_PAIR.BTC_TO_XLM,
                CURRENCY_PAIR.BTC_TO_TRX,
                CURRENCY_PAIR.BTC_TO_AION,
                CURRENCY_PAIR.BTC_TO_ITC,
                CURRENCY_PAIR.BTC_TO_ARK,
                CURRENCY_PAIR.BTC_TO_STRAT,
                CURRENCY_PAIR.BTC_TO_LSK,
                CURRENCY_PAIR.BTC_TO_ENG,
                CURRENCY_PAIR.BTC_TO_XVG,
                CURRENCY_PAIR.BTC_TO_ONT,
                CURRENCY_PAIR.BTC_TO_HSR,
                CURRENCY_PAIR.BTC_TO_ZIL,
                CURRENCY_PAIR.BTC_TO_VEN,
                CURRENCY_PAIR.BTC_TO_ELF,
                CURRENCY_PAIR.BTC_TO_BLZ,
                CURRENCY_PAIR.BTC_TO_REQ,
                CURRENCY_PAIR.BTC_TO_LINK,
                CURRENCY_PAIR.BTC_TO_NAS,
                CURRENCY_PAIR.BTC_TO_ELA,
                CURRENCY_PAIR.BTC_TO_NAS,
                CURRENCY_PAIR.BTC_TO_ELA,
                CURRENCY_PAIR.ETH_TO_DASH,
                CURRENCY_PAIR.ETH_TO_LTC,
                CURRENCY_PAIR.ETH_TO_XRP,
                CURRENCY_PAIR.ETH_TO_BCC,
                CURRENCY_PAIR.ETH_TO_ETC,
                CURRENCY_PAIR.ETH_TO_SC,
                CURRENCY_PAIR.ETH_TO_DGB,
                CURRENCY_PAIR.ETH_TO_XEM,
                CURRENCY_PAIR.ETH_TO_OMG,
                CURRENCY_PAIR.ETH_TO_ZEC,
                CURRENCY_PAIR.ETH_TO_REP,
                CURRENCY_PAIR.ETH_TO_XMR,
                CURRENCY_PAIR.ETH_TO_NEO,
                CURRENCY_PAIR.ETH_TO_QTUM,
                CURRENCY_PAIR.ETH_TO_EOS,
                CURRENCY_PAIR.ETH_TO_IOTA,
                CURRENCY_PAIR.ETH_TO_BTG,
                CURRENCY_PAIR.ETH_TO_WTC,
                CURRENCY_PAIR.ETH_TO_KNC,
                CURRENCY_PAIR.ETH_TO_BAT,
                CURRENCY_PAIR.ETH_TO_ZRX,
                CURRENCY_PAIR.ETH_TO_RDN,
                CURRENCY_PAIR.ETH_TO_GAS,
                CURRENCY_PAIR.ETH_TO_ADA,
                CURRENCY_PAIR.ETH_TO_RCN,
                CURRENCY_PAIR.ETH_TO_QSP,
                CURRENCY_PAIR.ETH_TO_XBY,
                CURRENCY_PAIR.ETH_TO_PAC,
                CURRENCY_PAIR.ETH_TO_RDD,
                CURRENCY_PAIR.ETH_TO_ICX,
                CURRENCY_PAIR.ETH_TO_WABI,
                CURRENCY_PAIR.ETH_TO_XLM,
                CURRENCY_PAIR.ETH_TO_TRX,
                CURRENCY_PAIR.ETH_TO_AION,
                CURRENCY_PAIR.ETH_TO_ITC,
                CURRENCY_PAIR.ETH_TO_ARK,
                CURRENCY_PAIR.ETH_TO_STRAT,
                CURRENCY_PAIR.ETH_TO_LSK,
                CURRENCY_PAIR.ETH_TO_ENG,
                CURRENCY_PAIR.ETH_TO_XVG,
                CURRENCY_PAIR.ETH_TO_ONT,
                CURRENCY_PAIR.ETH_TO_HSR,
                CURRENCY_PAIR.ETH_TO_ZIL,
                CURRENCY_PAIR.ETH_TO_VEN,
                CURRENCY_PAIR.ETH_TO_ELF,
                CURRENCY_PAIR.ETH_TO_BLZ,
                CURRENCY_PAIR.ETH_TO_REQ,
                CURRENCY_PAIR.ETH_TO_LINK,
                CURRENCY_PAIR.ETH_TO_NAS,
                CURRENCY_PAIR.ETH_TO_ELA,
                CURRENCY_PAIR.USD_TO_DASH,
                CURRENCY_PAIR.USD_TO_BTC,
                CURRENCY_PAIR.USD_TO_LTC,
                CURRENCY_PAIR.USD_TO_XRP,
                CURRENCY_PAIR.USD_TO_BCC,
                CURRENCY_PAIR.USD_TO_ETC,
                CURRENCY_PAIR.USD_TO_ETH,
                CURRENCY_PAIR.USD_TO_ZEC,
                CURRENCY_PAIR.USD_TO_REP,
                CURRENCY_PAIR.USD_TO_XMR,
                CURRENCY_PAIR.USDT_TO_DASH,
                CURRENCY_PAIR.USDT_TO_ETH,
                CURRENCY_PAIR.USDT_TO_LTC,
                CURRENCY_PAIR.USDT_TO_XRP,
                CURRENCY_PAIR.USDT_TO_BCC,
                CURRENCY_PAIR.USDT_TO_ETC,
                CURRENCY_PAIR.USDT_TO_SC,
                CURRENCY_PAIR.USDT_TO_DGB,
                CURRENCY_PAIR.USDT_TO_XEM,
                CURRENCY_PAIR.USDT_TO_ARDR,
                CURRENCY_PAIR.USDT_TO_BTC,
                CURRENCY_PAIR.USDT_TO_ZEC,
                CURRENCY_PAIR.USDT_TO_REP,
                CURRENCY_PAIR.USDT_TO_XMR,
                CURRENCY_PAIR.USDT_TO_NEO,
                CURRENCY_PAIR.USDT_TO_QTUM,
                CURRENCY_PAIR.USDT_TO_EOS,
                CURRENCY_PAIR.USDT_TO_IOTA,
                CURRENCY_PAIR.USDT_TO_BTG,
                CURRENCY_PAIR.USDT_TO_WTC,
                CURRENCY_PAIR.USDT_TO_KNC,
                CURRENCY_PAIR.USDT_TO_BAT,
                CURRENCY_PAIR.USDT_TO_ZRX,
                CURRENCY_PAIR.USDT_TO_RDN,
                CURRENCY_PAIR.USDT_TO_GAS,
                CURRENCY_PAIR.USDT_TO_ADA,
                CURRENCY_PAIR.USDT_TO_RCN,
                CURRENCY_PAIR.USDT_TO_QSP,
                CURRENCY_PAIR.USDT_TO_XBY,
                CURRENCY_PAIR.USDT_TO_PAC,
                CURRENCY_PAIR.USDT_TO_RDD,
                CURRENCY_PAIR.USDT_TO_ICX,
                CURRENCY_PAIR.USDT_TO_WABI,
                CURRENCY_PAIR.USDT_TO_XLM,
                CURRENCY_PAIR.USDT_TO_TRX,
                CURRENCY_PAIR.USDT_TO_AION,
                CURRENCY_PAIR.USDT_TO_ITC,
                CURRENCY_PAIR.USDT_TO_XVG,
                CURRENCY_PAIR.USDT_TO_OMG,
                CURRENCY_PAIR.USDT_TO_HSR,
                CURRENCY_PAIR.USDT_TO_ZIL,
                CURRENCY_PAIR.USDT_TO_VEN,
                CURRENCY_PAIR.USDT_TO_ELF,
                CURRENCY_PAIR.USDT_TO_NAS,
                CURRENCY_PAIR.USDT_TO_ELA,
                CURRENCY_PAIR.USD_TO_USDT]
