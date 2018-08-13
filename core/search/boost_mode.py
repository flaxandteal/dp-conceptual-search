from enum import Enum


class BoostMode(Enum):
    REPLACE = "replace"
    MULTIPLY = "multiply"
    SUM = "sum"
    AVG = "avg"
    MAX = "max"
    MIN = "min"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
