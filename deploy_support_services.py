from deploy.service_utils import deploy_telegram_notifier, deploy_order_storing, deploy_expired_order_processing, \
    deploy_failed_order_processing, deploy_bot_trades_retrieval


if __name__ == "__main__":
    # Create named screen
    screen_name = "common_crypto"

    # 1st stage - initialization of TG notifier
    deploy_telegram_notifier(screen_name=screen_name, should_create_screen=True)

    # # 2nd stage - initialization of Order saving service
    # deploy_order_storing(screen_name=screen_name, should_create_screen=False)
    #
    # # 3th stage - initialization of Expired order processing service
    # deploy_expired_order_processing(screen_name=screen_name, should_create_screen=False)
    #
    # # 4th stage - initialization of Expired order processing service
    # deploy_failed_order_processing(screen_name=screen_name, should_create_screen=False)
    #
    # # 5th stage - initialization of trades retrieval from exchanges
    # deploy_bot_trades_retrieval(screen_name=screen_name, should_create_screen=False)