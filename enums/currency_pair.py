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
    USD_TO_BTC = 2011

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
                CURRENCY_PAIR.ETH_TO_DASH,
                CURRENCY_PAIR.ETH_TO_LTC,
                CURRENCY_PAIR.ETH_TO_XRP,
                CURRENCY_PAIR.ETH_TO_BCC,
                CURRENCY_PAIR.ETH_TO_ETC,
                CURRENCY_PAIR.ETH_TO_SC,
                CURRENCY_PAIR.ETH_TO_DGB,
                CURRENCY_PAIR.ETH_TO_XEM,
                CURRENCY_PAIR.USD_TO_DASH,
                CURRENCY_PAIR.USD_TO_BTC,
                CURRENCY_PAIR.USD_TO_LTC,
                CURRENCY_PAIR.USD_TO_XRP,
                CURRENCY_PAIR.USD_TO_BCC,
                CURRENCY_PAIR.USD_TO_ETC,
                CURRENCY_PAIR.USD_TO_ETH
                ]
