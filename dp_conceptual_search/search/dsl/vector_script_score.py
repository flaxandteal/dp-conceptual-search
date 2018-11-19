"""
Defines a vector score query object
"""
from numpy import ndarray

from dp_conceptual_search.search.dsl.scripts import Scripts
from dp_conceptual_search.search.dsl.script_score import ScriptScore
from dp_conceptual_search.search.dsl.script_language import ScriptLanguage


class VectorScriptScore(ScriptScore):
    def __init__(self, field: str, vector: ndarray, cosine: bool=True):
        """
        Defines a vector score function to be used with the binary-vector-scoring Elasticsearch plugin
        :param field:
        :param vector:
        :param cosine:
        :param weight:
        """
        super(VectorScriptScore, self).__init__(**{
            "lang": ScriptLanguage.KNN.value,
            "params": {
                "cosine": cosine,
                "field": field,
                "vector": vector.tolist()
            },
            "script": Scripts.BINARY_VECTOR_SCORE.value
        })
