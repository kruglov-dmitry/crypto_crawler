import dao
# from dao.dao import sell_by_exchange, buy_by_exchange, parse_deal_id_by_exchange_id, \
#     get_method_for_create_url_trade_by_exchange_id

from data_access.classes.WorkUnit import WorkUnit
from data_access.message_queue import DEAL_INFO_MSG, DEBUG_INFO_MSG

from debug_utils import print_to_console, LOG_ALL_ERRORS, LOG_ALL_MARKET_NETWORK_RELATED_CRAP, ERROR_LOG_FILE_NAME

from enums.deal_type import DEAL_TYPE
from enums.exchange import EXCHANGE
from enums.status import STATUS

from utils.currency_utils import get_currency_pair_name_by_exchange_id
from utils.file_utils import log_to_file
from utils.key_utils import get_key_by_exchange
from utils.string_utils import float_to_str
from utils.time_utils import get_now_seconds_utc

# FIXME NOTE - global variables are VERY bad
# is it for SINGLE arbitrage process only, not overall!
overall_profit_so_far = 0.0


def init_deal(trade_to_perform, debug_msg):
    res = STATUS.FAILURE, None
    try:
        if trade_to_perform.trade_type == DEAL_TYPE.SELL:
            res = dao.sell_by_exchange(trade_to_perform)
        else:
            res = dao.buy_by_exchange(trade_to_perform)
    except Exception, e:
        msg = "init_deal: FAILED ERROR WE ALL DIE with following exception: {excp} {dbg}".format(excp=str(e),
                                                                                                 dbg=debug_msg)
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, ERROR_LOG_FILE_NAME)

    return res


def init_deals_with_logging(trade_pairs, difference, file_name, msg_queue):
    global overall_profit_so_far

    first_deal = trade_pairs.deal_1
    second_deal = trade_pairs.deal_2

    if second_deal.exchange_id == EXCHANGE.KRAKEN:
        # It is hilarious but if deal at kraken will not succeeded no need to bother with second exchange
        first_deal = trade_pairs.deal_2
        second_deal = trade_pairs.deal_1

    # market routine
    debug_msg = "Deals details: " + str(first_deal)
    result_1 = init_deal(first_deal, debug_msg)

    first_deal.execute_time = get_now_seconds_utc()

    if result_1[0] != STATUS.SUCCESS:
        msg = "Failing of adding FIRST deal! {deal}".format(deal=str(first_deal))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, ERROR_LOG_FILE_NAME)
        return STATUS.FAILURE

    debug_msg = "Deals details: " + str(second_deal)
    result_2 = init_deal(second_deal, debug_msg)

    second_deal.execute_time = get_now_seconds_utc()

    if result_1[0] == STATUS.FAILURE or result_2[0] == STATUS.FAILURE:
        msg = "Failing of adding deals! {deal_pair}".format(deal_pair=str(trade_pairs))
        print_to_console(msg, LOG_ALL_ERRORS)
        log_to_file(msg, ERROR_LOG_FILE_NAME)
        return STATUS.FAILURE

    overall_profit_so_far += trade_pairs.current_profit

    msg = "Some deals sent to exchanges. Expected profit: {cur}. Overall: {tot} Difference in percents: " \
          "{diff} Deal details: {deal}".format(cur=float_to_str(trade_pairs.current_profit),
                                               tot=float_to_str(overall_profit_so_far),
                                               diff=difference, deal=str(trade_pairs))

    print_to_console(msg, LOG_ALL_MARKET_NETWORK_RELATED_CRAP)
    log_to_file(trade_pairs, file_name)

    msg_queue.add_message(DEAL_INFO_MSG, msg)

    return STATUS.SUCCESS


def init_deals_with_logging_speedy_fake(trade_pairs, difference, file_name, processor):
    pass


def return_with_no_change(json_document, corresponding_trade):
    corresponding_trade.execute_time = get_now_seconds_utc()
    corresponding_trade.deal_id = dao.parse_deal_id_by_exchange_id(corresponding_trade.exchange_id, json_document)
    return json_document, corresponding_trade


def init_deals_with_logging_speedy(trade_pairs, difference, file_name, processor, msg_queue):
    parallel_deals = []

    for trade in [trade_pairs.deal_1, trade_pairs.deal_2]:
        method_for_url = dao.get_method_for_create_url_trade_by_exchange_id(trade)
        # key, pair_name, price, amount
        key = get_key_by_exchange(trade.exchange_id)
        pair_name = get_currency_pair_name_by_exchange_id(trade.pair_id, trade.exchange_id)
        post_details = method_for_url(key, pair_name, trade.price, trade.volume)
        constructor = return_with_no_change

        wu = WorkUnit(post_details.final_url, constructor, trade)
        wu.add_post_details(post_details)

        parallel_deals.append(wu)

    res = processor.process_async_post(parallel_deals, DEAL_MAX_TIMEOUT)

    global overall_profit_so_far
    overall_profit_so_far += trade_pairs.current_profit

    msg = """ <b> DEMO MODE ON </b>
        We try to send following deals to exchange.
    <b>Expected profit:</b> <i>{cur}</i>.
    <b>Overall:</b> <i>{tot}</i>
    <b>Difference in percents:</b> <i>{diff}</i>

            Deal details:
    {deal}
    """.format(cur=float_to_str(trade_pairs.current_profit), tot=float_to_str(overall_profit_so_far),
               diff=difference, deal=str(trade_pairs))

    msg_queue.add_message(DEAL_INFO_MSG, msg)
    log_to_file(msg, file_name)

    # check for errors only
    for (return_value, trade) in res:
        # check for none and error_code may not be jsonable
        if return_value.status_code == 200:
            msg = """ For trade {trade}
            Response is {resp} """.format(trade=trade, resp=return_value.json())
        else:
            response_json = "Not provided"
            try:
                response_json = return_value.json()
            except:
                pass
            msg = """ For trade {trade}
            Response is <b>BAD CODE!</b> {resp} and exact json - {js}""".format(trade=trade,
                                                                                resp=str(return_value.status_code),
                                                                                js=response_json)

        print_to_console(msg, LOG_ALL_ERRORS)
        msg_queue.add_message(DEBUG_INFO_MSG, msg)
        log_to_file(msg, file_name)
