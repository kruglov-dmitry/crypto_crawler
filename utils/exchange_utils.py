from enums.exchange import EXCHANGE

def get_exchange_name_by_id(exchange_id):
    return {
        EXCHANGE.POLONIEX: "POLONIEX",
        EXCHANGE.KRAKEN: "KRAKEN",
        EXCHANGE.BITTREX: "BITTREX",
    }[exchange_id]