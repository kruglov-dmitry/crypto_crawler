class WorkUnit:
    def __init__(self, url, method, *args):
        self.url = url
        self.method = method
        self.args = args

    def add_future(self, some_future):
        self.future_result = some_future

    def add_post_details(self, post_details):
        self.post_details = post_details

    def add_http_method(self, http_method):
        self.http_method = http_method