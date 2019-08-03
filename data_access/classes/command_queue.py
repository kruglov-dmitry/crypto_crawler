from data_access.classes.redis_connection import RedisConnection


class CommandQueue(RedisConnection):
    """
        Bidirectional channel for communication between following entities:
            puppeteer
            node_puppeteer
            and maybe agents
    """
    def register_node(self, server_name):
        self.p = self.r.pubsub()
        self.p.subscribe(server_name)
        return self.p

    def get_list_of_nodes(self):
        self.r.pubsub_channels()

    def get_command(self):
        message = self.p.get_message()
        if message:
            return message['data']

        return None
