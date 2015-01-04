from collections import Iterable
from copy import deepcopy
import time

__author__ = 'thiagovieira'


def flatten(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, basestring):
            for x in flatten(item):
                yield x
        else:
            if item != 'binary':
                yield item
            else:
                continue


def new_deepcopy(obj):  # deep copy (recursive) of simple dictionary/list types
    if isinstance(obj, dict):
        d = obj.copy()  # shallow dict copy
        for k, v in d.iteritems():
            d[k] = deepcopy(v)
    elif isinstance(obj, (list, tuple)):
        d = obj[:]  # shallow list/tuple copy
        i = len(d)
        while i:
            i -= 1
            d[i] = deepcopy(d[i])
    else:
        d = obj  # a string, an int, or whatever
    return d


class timewith():
    def __init__(self, name=''):
        self.name = name
        self.start = time.clock()  # unix user time.time(), windows use time.clock()

    @property
    def elapsed(self):
        return time.clock() - self.start  # unix user time.time(), windows use time.clock()

    def checkpoint(self, name=''):
        print '{timer} {checkpoint} took {elapsed} seconds'.format(
            timer=self.name,
            checkpoint=name,
            elapsed=self.elapsed,
        ).strip()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.checkpoint('finished')
        pass
