from requests import Session
from bittrex.socket_api import WebSocketConnection

from websocket import create_connection
import zlib
import websocket
import time
import ssl


def test_bittrex():
    with Session() as session:
        session.auth = HTTPBasicAuth("known", "user")
        connection = WebSocketConnection("http://localhost:5000/signalr", session)
        chat = connection.register_hub('chat')

        def print_received_message(data):
            print('received: ', data)

        def print_topic(topic, user):
            print('topic: ', topic, user)

        def print_error(error):
            print('error: ', error)

        chat.client.on('newMessageReceived', print_received_message)
        chat.client.on('topicChanged', print_topic)

        connection.error += print_error

        with connection:
            chat.server.invoke('send', 'Python is here')
            chat.server.invoke('setTopic', 'Welcome python!')
            chat.server.invoke('requestError')
            chat.server.invoke('send', 'Bye-bye!')

            connection.wait(1)

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


if __name__ == "__main__":
    pass