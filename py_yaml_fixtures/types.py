from typing import *


class Identifier:
    def __init__(self, class_name: str, key: Union[int, str]):
        self.class_name = class_name
        self.key = key

    def __iter__(self):
        return iter([self.class_name, self.key])

    def __repr__(self):
        return '{cls}({key})'.format(cls=self.class_name, key=self.key)


class AttrDict:
    __slots__ = ('_d',)

    def __init__(self, dict_):
        self._d = dict_

    def __getitem__(self, item):
        return self._d[item]

    def __setitem__(self, key, value):
        self._d[key] = value

    def __contains__(self, item):
        return item in self._d

    def __getattr__(self, item):
        if item in self._d:
            return self._d[item]
        raise AttributeError(item)

    def __setattr__(self, key, value):
        if key in self.__slots__:
            return super().__setattr__(key, value)
        self._d[key] = value
