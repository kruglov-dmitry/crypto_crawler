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
                CURRENCY_PAIR.USD_TO_XMR
                ]
