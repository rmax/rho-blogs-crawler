import datetime


class StringToDatetime(object):
    def __init__(self, format):
        self.format = format

    def __call__(self, value):
        return datetime.datetime.strptime(value, self.format)
