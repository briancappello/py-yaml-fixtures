from typing import *


class Identifier:
    def __init__(self, class_name: str, key: Union[int, str]):
        self.class_name = class_name
        self.key = key

    def __iter__(self):
        return iter([self.class_name, self.key])

    def __repr__(self):
        return '{cls}({key})'.format(cls=self.class_name, key=self.key)

    def __eq__(self, other):
        if not isinstance(other, Identifier):
            return False
        return self.class_name == other.class_name and self.key == other.key

    def __ne__(self, other):
        return not self.__eq__(other)
