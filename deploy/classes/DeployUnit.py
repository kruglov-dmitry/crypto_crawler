from data.BaseData import BaseData


class DeployUnit(BaseData):
    def __init__(self, screen_name, window_name, command):
        self.screen_name = screen_name
        self.window_name = window_name
        self.command = command