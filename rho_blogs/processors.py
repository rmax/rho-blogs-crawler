from __future__ import with_statement

import datetime
import locale

from contextlib import contextmanager

@contextmanager
def use_locale(value, category=locale.LC_ALL):
    original = locale.getlocale()
    locale.setlocale(category, value)
    yield
    locale.setlocale(category, original)


class StringToDatetime(object):
    def __init__(self, format, locale=None):
        self.format = format
        self.locale = locale

    def __call__(self, value):
        # strptime only likes str but not unicode
        value = value.encode('utf-8')
        if self.locale is None:
            return datetime.datetime.strptime(value, self.format)
        else:
            with use_locale(self.locale):
                return datetime.datetime.strptime(value, self.format)

