class WorkUnit:
    def __init__(self, url, method, *args):
        self.url = url
        self.method = method
        self.args = args

        self.future_result = None
        self.post_details = None
        self.http_method = None

    def add_future(self, some_future):
        self.future_result = some_future

    def add_post_details(self, post_details):
        self.post_details = post_details

    def add_http_method(self, http_method):
        self.http_method = http_method

    @property
    def future_value(self):
        return self.future_result.value

    @property
    def future_value_json(self):
        return self.future_result.value.json()

    @property
    def future_status_code(self):
        return self.future_result.value.status_code
