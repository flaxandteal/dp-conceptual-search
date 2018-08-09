from enum import Enum
from elasticsearch_dsl import query as Q


class RescoreQuery(Q.Query):
    name = "rescore"


class ScriptScore(Q.Query):
    name = "script_score"


class FunctionScore(Q.Query):
    name = "function_score"


class Scripts(Enum):
    BINARY_VECTOR_SCORE = "binary_vector_score"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ScriptLanguage(Enum):
    KNN = "knn"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


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
