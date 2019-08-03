class EXCHANGE(object):
    POLONIEX = 1
    POLONIEX_EXCHANGE = "POLONIEX"

    KRAKEN = 2
    KRAKEN_EXCHANGE = "KRAKEN"

    BITTREX = 3
    BITTREX_EXCHANGE = "BITTREX"

    BINANCE = 4
    BINANCE_EXCHANGE = "BINANCE"

    HUOBI = 5
    HUOBI_EXCHANGE = "HUOBI"

    @classmethod
    def values(cls):
        return [EXCHANGE.POLONIEX,
                EXCHANGE.KRAKEN,
                EXCHANGE.BITTREX,
                EXCHANGE.BINANCE,
                EXCHANGE.HUOBI]

    @classmethod
    def exchange_names(cls):
        return [EXCHANGE.POLONIEX_EXCHANGE, EXCHANGE.KRAKEN_EXCHANGE, EXCHANGE.BITTREX_EXCHANGE,
                EXCHANGE.BINANCE_EXCHANGE, EXCHANGE.HUOBI_EXCHANGE]


# In percents
EXCHANGE_FEE = {EXCHANGE.POLONIEX: 0.25,
                EXCHANGE.KRAKEN: 0.26,
                EXCHANGE.BITTREX: 0.25,
                EXCHANGE.BINANCE: 0.1,
                EXCHANGE.HUOBI: 0.2}

