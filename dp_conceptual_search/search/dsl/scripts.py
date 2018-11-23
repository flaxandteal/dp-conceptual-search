"""
Enum of available scripts
"""
from enum import Enum


class Scripts(Enum):
    BINARY_VECTOR_SCORE = "binary_vector_score"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
