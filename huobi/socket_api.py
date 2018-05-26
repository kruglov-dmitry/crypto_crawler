import websocket
import ssl

import zlib
import uuid

from huobi.currency_utils import get_currency_pair_to_huobi


def process_message(compressData):
    return zlib.decompress(compressData, 16 + zlib.MAX_WBITS).decode('utf-8')


class HuobiParameters:
    URL = "wss://api.huobipro.com/ws"
    SUBSCRIPTION_STRING = """{"sub": "market.{pair_name}.depth.step0","id": "{uuid_id}"}"""


def default_on_public(args):
    print "on_public", args
    msg = process_message(args)
    print msg


class SubscriptionHuobi:
    def __init__(self, pair_id, base_url=HuobiParameters.URL,
                 on_update=default_on_public):
        """
        :param pair_id:     - currency pair to be used for trading
        :param base_url:    - web-socket subscription end points
        :param on_receive:  - pass
        :param on_error:    - recconect
        :param on_update:   - idea is the following:
            we pass reference to method WITH initialized order book for that pair_id
            whenever we receive update we update order book and trigger checks for arbitrage
        """

        self.url = base_url

        self.pair_id = pair_id
        self.pair_name = get_currency_pair_to_huobi(self.pair_id)

        self.subscription_url = HuobiParameters.SUBSCRIPTION_STRING.format(pair_name=self.pair_name, uuid_id=uuid.uuid4())

        self.on_update = on_update

    def on_public(self, args):
        print "on_public", args
        msg = process_message(args)
        self.on_update(msg)

    def subscribe(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(HuobiParameters.URL + self.subscription_url)

        ws.on_message = self.on_public

        ws.on_error = self.subscribe

        ws.on_close = default_on_public
        ws.on_open = default_on_public

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
