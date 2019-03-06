from requests import Session
from signalr import Connection

from websocket import create_connection
import zlib
import websocket
import time
import ssl

import thread
import json

from zlib import decompress, MAX_WBITS
from json import loads
from base64 import b64decode

from bittrex.socket_api import BittrexParameters
from utils.file_utils import log_to_file

from utils.time_utils import get_now_seconds_utc_ms 


order_book_is_received = True


def test_bittrex():
    def process_message(message):
        deflated_msg = decompress(b64decode(message), -MAX_WBITS)
        return loads(deflated_msg.decode())

    def on_receive(**kwargs):
        global order_book_is_received 
        # print "on_receive", kwargs
        if 'R' in kwargs and type(kwargs['R']) is not bool:
            msg = process_message(kwargs['R'])
            if msg is not None:
                order_book_is_received = False
                with open('data.json', 'w') as outfile:
                    json.dump(msg, outfile)
        else:
            if order_book_is_received:
                time.sleep(5)

    def on_public(args):
        # print "on_public", args
        msg = process_message(args)
        if msg is not None:
            print msg

    def on_private(args):
        # print 100
        pass

    # create error handler
    def print_error(error):
        print('error: ', error)

    with Session() as session:
        connection = Connection("https://socket.bittrex.com/signalr", session)
        hub = connection.register_hub('c2')

        connection.received += on_receive

        hub.client.on(BittrexParameters.MARKET_DELTA, on_public)
        
        connection.error += print_error

        connection.start()

        while order_book_is_received:
            hub.server.invoke("QueryExchangeState", "BTC-ETH")

        print "Order book should be received at this stage"

        while connection.started:
            hub.server.invoke("SubscribeToExchangeDeltas", "BTC-ETH")


def test_huobi():
    def process_result(result):
        result = zlib.decompress(compressData, 16 + zlib.MAX_WBITS).decode('utf-8')
        if result[:7] == '{"ping"':
            ts = result[8:21]
            pong = '{"pong":' + ts + '}'
            ws.send(pong)
            ws.send(tradeStr)
        return result

    while(1):
        try:
            ws = create_connection("wss://api.huobipro.com/ws")
            ws.settimeout(1)
            break
        except:
            print('connect ws error,retry...')
            time.sleep(5)

    tradeStr="""{"sub": "market.ethbtc.depth.step0","id": "id10"}"""

    ws.send(tradeStr)
    compressData=ws.recv()
    print "CONFIRMATION OF SUBSCRIPTION:", process_result(compressData)
    raise

    while(1):
        try:
            compressData=ws.recv()
            print "DELTA?", process_result(compressData)
        except Exception as e:
            print "EXCEPTION:", e 
            break


def test_binance():
    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        print("ONOPEN")
        # def run(*args):
        #     ws.send(json.dumps({'command':'subscribe','channel':'BTC-ETH@depth'}))
        #     while True:
        #         time.sleep(1)
        #     ws.close()
        #     print("thread terminating...")
        # thread.start_new_thread(run, ())

    # websocket.enableTrace(True)
    # # ws = websocket.WebSocketApp(sslopt={"cert_reqs": ssl.CERT_NONE})
    # ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/ethbtc@depth")
    # # ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    # ws.on_message = on_message
    # ws.on_error = on_error
    # ws.on_close = on_close
    # ws.on_open = on_open
    # # ws.connect("wss://stream.binance.com:9443/ws/ethbtc@depth")
    # # ws.run_forever()
    # ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


    # Create connection
    while True:
        try:
            ws = create_connection("wss://stream.binance.com:9443/ws/ethbtc@depth", sslopt={"cert_reqs": ssl.CERT_NONE})
            ws.settimeout(15)
            break
        except:
            print('connect ws error,retry...')
            sleep_for(5)

    # actual subscription
    # ws.send()

    # event loop
    while True:
        try:
            compressData = ws.recv()
            on_message(ws, compressData)
        except Exception as e:      # Supposedly timeout big enough to not trigger re-syncing
            msg = "Binance - triggered exception during reading from socket = {}".format(str(e))
            print msg
            break

    msg = "Binance - triggered on_close. We have to re-init the whole state from the scratch. Current thread will be finished."
    log_to_file(msg, SOCKET_ERRORS_LOG_FILE_NAME)


first_responce = False

def test_poloniex():
    def on_message(ws, msg):
        global first_responce
        name = "poloniex-" + str(get_now_seconds_utc_ms()) + ".json"
    
        with open(name, 'w') as outfile:
            j = json.loads(msg)
            json.dump(j, outfile)

        if "orderBook" in msg and not first_responce:
            first_responce = True
        else:
            print(msg)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        print("ONOPEN")
        # global first_responce

        def run(*args):
            ws.send(json.dumps({'command': 'subscribe', 'channel': 1001}))
            # ws.send(json.dumps({'command': 'subscribe', 'channel': 1002}))
            # ws.send(json.dumps({'command': 'subscribe', 'channel': 1003}))
            ws.send(json.dumps({'command': 'subscribe', 'channel': 'BTC_ETH'}))
            
            # while not first_responce:
            while True:
                time.sleep(1)

            ws.close()
            print("thread terminating...")

        thread.start_new_thread(run, ())

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api2.poloniex.com/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

def test_poloniex_advanced():
    import threading
    from enums.currency_pair import CURRENCY_PAIR
    from poloniex.socket_api import SubscriptionPoloniex

    t1 = SubscriptionPoloniex(CURRENCY_PAIR.BTC_TO_ETC)
    t1.subscribe()

    # buy_subscription_thread = threading.Thread(target=t1.subscribe, args=())
    # buy_subscription_thread.daemon = True
    # buy_subscription_thread.start()
    #
    # return t1

def test_bittrex_advanced():
    from enums.currency_pair import CURRENCY_PAIR
    from bittrex.socket_api import SubscriptionBittrex
    import threading
    from data_access.memory_cache import get_cache

    t1 = SubscriptionBittrex(CURRENCY_PAIR.BTC_TO_ETC)
    # t1.subscribe()

    buy_subscription_thread = threading.Thread(target=t1.subscribe, args=())
    buy_subscription_thread.daemon = True
    buy_subscription_thread.start()


def test_huobi_advanced():
    import threading
    from enums.currency_pair import CURRENCY_PAIR
    from huobi.socket_api import SubscriptionHuobi
    t1 = SubscriptionHuobi(CURRENCY_PAIR.BTC_TO_ETC)
    # t1.subscribe()

    buy_subscription_thread = threading.Thread(target=t1.subscribe, args=())
    buy_subscription_thread.daemon = True
    buy_subscription_thread.start()

    return t1


def test_binance_advanced():
    import threading
    from enums.currency_pair import CURRENCY_PAIR
    from binance.socket_api import SubscriptionBinance
    t1 = SubscriptionBinance(CURRENCY_PAIR.BTC_TO_ETC)
    # t1.subscribe()
    buy_subscription_thread = threading.Thread(target=t1.subscribe, args=())
    buy_subscription_thread.daemon = True
    buy_subscription_thread.start()

    return t1


if __name__ == "__main__":
    from utils.time_utils import sleep_for
    # test_huobi()
    # w = test_huobi_advanced()
    # sleep_for(10)
    # w.disconnect()
    # print(w.should_run)

    # test_poloniex()
    w = test_poloniex_advanced()
    # sleep_for(10)
    # w.disconnect()
    # print(w.should_run)

    # test_binance()
    # w = test_binance_advanced()
    # sleep_for(10)
    # w.disconnect()
    # print(w.should_run)

    # test_bittrex_advanced()


    # while 1:
    #     print "WTF"
    #     sleep_for(10)

    # cnt = 0
    # while True:
    #     sleep_for(10)
    #     cnt += 1
    #     if cnt == 5:
    #         w.disconnect()
