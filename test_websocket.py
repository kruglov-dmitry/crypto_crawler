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




def sketch():

    from enums.exchange import EXCHANGE

    def my_print(w):
        print w

    ws1 = WebSocket("https://socket.bittrex.com/signalr", EXCHANGE.BITTREX, my_print)
    ws2 = WebSocket("wss://api2.poloniex.com/", EXCHANGE.POLONIEX, my_print)

    pair_id = None

    ws1.subscribe(pair_id)
    ws2.subscribe(pair_id)

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
        #hub.client.on(BittrexParameters.SUMMARY_DELTA, on_public)
        #hub.client.on(BittrexParameters.SUMMARY_DELTA_LITE, on_public)
        # hub.client.on(BittrexParameters.BALANCE_DELTA, on_private)
        # hub.client.on(BittrexParameters.ORDER_DELTA, on_private)
        
        connection.error += print_error

        connection.start()

        while order_book_is_received:
            hub.server.invoke("QueryExchangeState", "BTC-ETH")

        print "Done"

        # with connection:
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
            break
        except:
            print('connect ws error,retry...')
            time.sleep(5)

    tradeStr="""{"sub": "market.ethbtc.depth.step0","id": "id10"}"""

    ws.send(tradeStr)
    compressData=ws.recv()
    print "CONFIRMATION OF SUBSCRIPTION:", process_result(compressData)

    while(1):
        compressData=ws.recv()
        print "DELTA?", process_result(compressData)


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

    websocket.enableTrace(True)
    # ws = websocket.WebSocketApp(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/ethbtc@depth")
    # ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.on_message = on_message
    ws.on_error = on_error
    ws.on_close = on_close
    ws.on_open = on_open
    # ws.connect("wss://stream.binance.com:9443/ws/ethbtc@depth")
    # ws.run_forever()
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def test_poloniex():
    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        print("ONOPEN")

        def run(*args):
            ws.send(json.dumps({'command': 'subscribe', 'channel': 1001}))
            # ws.send(json.dumps({'command': 'subscribe', 'channel': 1002}))
            # ws.send(json.dumps({'command': 'subscribe', 'channel': 1003}))
            ws.send(json.dumps({'command': 'subscribe', 'channel': 'BTC_ETH'}))
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

if __name__ == "__main__":
    test_bittrex()
