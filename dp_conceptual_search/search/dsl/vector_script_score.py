"""
Defines a vector score query object
"""
from typing import List

from dp_conceptual_search.search.dsl.scripts import Scripts
from dp_conceptual_search.search.dsl.script_score import ScriptScore
from dp_conceptual_search.search.dsl.script_language import ScriptLanguage


class VectorScriptScore(ScriptScore):
    def __init__(self, field: str, vector: List[float], cosine: bool=True, weight: float=1.0):
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
                "vector": vector
            },
            "script": Scripts.BINARY_VECTOR_SCORE.value,
            "weight": weight
        })
