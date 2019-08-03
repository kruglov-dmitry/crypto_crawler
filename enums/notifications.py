class NOTIFICATION(object):
    ARBITRAGE = 1
    ARBITRAGE_NAME = "ARBITRAGE"

    DEBUG = 2
    DEBUG_NAME = "DEBUG"

    DEAL = 3
    DEAL_NAME = "DEAL"

    @classmethod
    def values(cls):
        return [NOTIFICATION.ARBITRAGE, NOTIFICATION.DEBUG, NOTIFICATION.DEAL]

    @classmethod
    def exchange_names(cls):
        return [NOTIFICATION.ARBITRAGE_NAME, NOTIFICATION.DEBUG_NAME, NOTIFICATION.DEAL_NAME]


def get_notification_name_by_id(notification_id):
    return {
        NOTIFICATION.ARBITRAGE: NOTIFICATION.ARBITRAGE_NAME,
        NOTIFICATION.DEAL: NOTIFICATION.DEAL_NAME,
        NOTIFICATION.DEBUG: NOTIFICATION.DEBUG_NAME
    }[notification_id]


def get_notification_id_by_name(notification_name):
    return {
        NOTIFICATION.ARBITRAGE_NAME: NOTIFICATION.ARBITRAGE,
        NOTIFICATION.DEAL_NAME: NOTIFICATION.DEAL,
        NOTIFICATION.DEBUG_NAME: NOTIFICATION.DEBUG
    }[notification_name]
