"""
Contains an enum of available script languages for ONS queries
"""
from enum import Enum


class ScriptLanguage(Enum):
    KNN = "knn"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
