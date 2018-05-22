from elasticsearch_dsl import query as Q

from enum import Enum
from numpy import ndarray

from server.search import fields
from server.word_embedding.supervised_models import SupervisedModel


def vector_script_score(field: fields.Field, vector: ndarray) -> dict:
    params = {
        "cosine": True,
        "field": field.name,
        "vector": vector.tolist()
    }
    script_score = {
        "lang": ScriptLanguage.KNN.value,
        "params": params,
        "script": Scripts.BINARY_VECTOR_SCORE.value
    }

    return script_score


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

    return terms


def content_query(search_term, model: SupervisedModel) -> Q.Query:
    from server.search.queries import content_query

    query = content_query(search_term)
    terms_query = word_vector_keywords_query(search_term, model)

    query = Q.DisMax(queries=[query, terms_query])

    return query
