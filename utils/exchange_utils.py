from enums.exchange import EXCHANGE, EXCHANGE_FEE


def get_exchange_name_by_id(exchange_id):
    return {
        EXCHANGE.POLONIEX: EXCHANGE.POLONIEX_EXCHANGE,
        EXCHANGE.KRAKEN: EXCHANGE.KRAKEN_EXCHANGE,
        EXCHANGE.BITTREX: EXCHANGE.BITTREX_EXCHANGE,
        EXCHANGE.BINANCE: EXCHANGE.BINANCE_EXCHANGE
    }[exchange_id]


def get_exchange_id_by_name(exchange_name):
    return {
        EXCHANGE.POLONIEX_EXCHANGE: EXCHANGE.POLONIEX,
        EXCHANGE.KRAKEN_EXCHANGE: EXCHANGE.KRAKEN,
        EXCHANGE.BITTREX_EXCHANGE: EXCHANGE.BITTREX,
        EXCHANGE.BINANCE_EXCHANGE: EXCHANGE.BINANCE
    }[exchange_name]


def get_fee_by_exchange(exchange_id):
    return EXCHANGE_FEE[exchange_id]