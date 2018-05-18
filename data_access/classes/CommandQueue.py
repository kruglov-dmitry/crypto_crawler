import redis as _redis
import pickle

class CommandQueue:
    """
        Bidirectional channel for communication between following entities:
            puppeteer
            node_puppeteer
            and maybe agents
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.r = _redis.StrictRedis(host=self.host, port=self.port, db=0)

    def register_node(self, server_name):
        p = self.r.pubsub()
        p.subscribe(server_name)
        return p

    def get_list_of_nodes(self):
        self.r.pubsub_channels()

    def get_command(self):
        message = p.get_message()
        if message:
            message['data']