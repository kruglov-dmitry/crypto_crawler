class CURRENCY_PAIR:
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

    BTC_TO_NEO = 17
    BTC_TO_QTUM = 18
    BTC_TO_EOS = 19
    BTC_TO_IOTA = 20
    BTC_TO_BTG = 21
    BTC_TO_WTC = 22
    BTC_TO_KNC = 23
    BTC_TO_BAT = 24
    BTC_TO_ZRX = 25
    BTC_TO_RDN = 26
    BTC_TO_GAS = 27
    BTC_TO_ADA = 28
    BTC_TO_RCN = 29
    BTC_TO_QSB = 30         # Not exist on binance
    BTC_TO_XBY = 31         # Not exist on binance
    BTC_TO_PAC = 32         # Not exist on binance
    BTC_TO_RDD = 33         # Not exist on binance
    BTC_TO_ICX = 34
    BTC_TO_WABI = 35
    BTC_TO_XLM = 36
    BTC_TO_TRX = 37
    BTC_TO_AION = 38
    BTC_TO_ITC = 39         # Not exist on binance

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

    ETH_TO_NEO = 1015       #
    ETH_TO_QTUM = 1016      #
    ETH_TO_EOS = 1017       #
    ETH_TO_IOTA = 1018
    ETH_TO_BTG = 1019
    ETH_TO_WTC = 1020
    ETH_TO_KNC = 1021
    ETH_TO_BAT = 1022
    ETH_TO_ZRX = 1023
    ETH_TO_RDN = 1024
    ETH_TO_GAS = 1025       # Not exist on binance
    ETH_TO_ADA = 1026
    ETH_TO_RCN = 1027
    ETH_TO_QSB = 1028       # Not exist on binance
    ETH_TO_XBY = 1029       # Not exist on binance
    ETH_TO_PAC = 1030       # Not exist on binance
    ETH_TO_RDD = 1031       # Not exist on binance
    ETH_TO_ICX = 1032
    ETH_TO_WABI = 1033
    ETH_TO_XLM = 1034
    ETH_TO_TRX = 1035
    ETH_TO_AION = 1036
    ETH_TO_ITC = 1037       # Not exist on binance

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
    # NOTE: NO OMG!
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
    USDT_TO_QSB = 3028
    USDT_TO_XBY = 3029
    USDT_TO_PAC = 3030
    USDT_TO_RDD = 3031
    USDT_TO_ICX = 3032
    USDT_TO_WABI = 3033
    USDT_TO_XLM = 3034
    USDT_TO_TRX = 3035
    USDT_TO_AION = 3036
    USDT_TO_ITC = 3037

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
                CURRENCY_PAIR.BTC_TO_QSB,
                CURRENCY_PAIR.BTC_TO_XBY,
                CURRENCY_PAIR.BTC_TO_PAC,
                CURRENCY_PAIR.BTC_TO_RDD,
                CURRENCY_PAIR.BTC_TO_ICX,
                CURRENCY_PAIR.BTC_TO_WABI,
                CURRENCY_PAIR.BTC_TO_XLM,
                CURRENCY_PAIR.BTC_TO_TRX,
                CURRENCY_PAIR.BTC_TO_AION,
                CURRENCY_PAIR.BTC_TO_ITC,
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
                CURRENCY_PAIR.USD_TO_USDT
                ]
