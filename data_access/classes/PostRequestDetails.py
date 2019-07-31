from data.base_data import BaseData


class PostRequestDetails(BaseData):
    def __init__(self, final_url, headers, body):
        self.final_url = final_url
        self.headers = headers
        self.body = body