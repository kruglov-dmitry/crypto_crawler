from enums.exchange import EXCHANGE, EXCHANGE_FEE
from logging_tools.exchange_util_logging import log_wrong_exchange_id


def get_exchange_name_by_id(exchange_id):
    return {
        EXCHANGE.POLONIEX: EXCHANGE.POLONIEX_EXCHANGE,
        EXCHANGE.KRAKEN: EXCHANGE.KRAKEN_EXCHANGE,
        EXCHANGE.BITTREX: EXCHANGE.BITTREX_EXCHANGE,
        EXCHANGE.BINANCE: EXCHANGE.BINANCE_EXCHANGE,
        EXCHANGE.HUOBI: EXCHANGE.HUOBI_EXCHANGE
    }[exchange_id]


def get_exchange_id_by_name(exchange_name):
    return {
        EXCHANGE.POLONIEX_EXCHANGE: EXCHANGE.POLONIEX,
        EXCHANGE.KRAKEN_EXCHANGE: EXCHANGE.KRAKEN,
        EXCHANGE.BITTREX_EXCHANGE: EXCHANGE.BITTREX,
        EXCHANGE.BINANCE_EXCHANGE: EXCHANGE.BINANCE,
        EXCHANGE.HUOBI_EXCHANGE: EXCHANGE.HUOBI
    }[exchange_name.upper()]


def get_fee_by_exchange(exchange_id):
    return EXCHANGE_FEE[exchange_id]


def parse_exchange_ids(exchange_list):
    ids_list = [x.strip() for x in exchange_list.split(',') if x.strip()]

    exchanges_ids = []
    for exchange_name in ids_list:
        new_exchange_id = get_exchange_id_by_name(exchange_name)
        if new_exchange_id in EXCHANGE.values():
            exchanges_ids.append(new_exchange_id)
        else:
            log_wrong_exchange_id(new_exchange_id)

            assert new_exchange_id in EXCHANGE.values()

    return exchanges_ids