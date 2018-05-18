from elasticsearch_dsl import query as Q

from enum import Enum

from server.search import fields
from server.word_embedding.supervised_models import SupervisedModel


class ScriptScore(Q.Query):
    name = "script_score"


class FunctionScore(Q.Query):
    name = "function_score"


class Scripts(Enum):
    BINARY_VECTOR_SCORE = "binary_vector_score"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class ScriptLanguage(Enum):
    KNN = "knn"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def word_vector_keywords_query(
        search_term: str,
        model: SupervisedModel) -> Q.Query:
    search_vector = model.get_sentence_vector(search_term)
    additional_keywords, similarity = model.get_labels_for_vector(
        search_vector, 10)
    additional_keywords = [k.replace("_", " ")
                           for k in additional_keywords]

    # Insert the original search term
    additional_keywords.insert(0, search_term)

    terms = Q.Terms(**{fields.keywords.name: additional_keywords})

    # Add query to dis_max
    keywords_query = Q.Bool(should=[Q.Match(**{fields.title.name: search_term}), terms])
    return keywords_query


def word_vector_function_score(search_term, model: SupervisedModel) -> Q.Query:
    wv = model.get_sentence_vector(search_term)

    query = word_vector_keywords_query(search_term, model)

    params = {
        "cosine": True,
        "field": fields.embedding_vector.name,
        "vector": wv.tolist()
    }
    script_score = {
        "lang": ScriptLanguage.KNN.value,
        "params": params,
        "script": Scripts.BINARY_VECTOR_SCORE.value
    }
    q = FunctionScore(query=query, boost_mode="replace", script_score=script_score)

    return q
