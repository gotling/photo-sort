from enum import Enum


class Mode(Enum):
    copy = 0
    move = 1
    replace = 2

    def __str__(self):
        return self.name


class Encode(Enum):
    no = 0
    yes = 1
    later = 2

    def __str__(self):
        return self.name
