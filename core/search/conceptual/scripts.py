from enum import Enum


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
