class BaseData(object):
    def __init__(self):
        pass

    def __str__(self):
        attr_list = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        str_repr = "["
        for every_attr in attr_list:
            str_repr += every_attr + " - " + str(getattr(self, every_attr)) + " "

        str_repr += "]"

        return str_repr