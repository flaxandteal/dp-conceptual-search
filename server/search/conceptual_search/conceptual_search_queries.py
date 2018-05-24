from elasticsearch_dsl import query as Q

from enum import Enum
from numpy import ndarray

from server.search import fields
from server.word_embedding.supervised_models import SupervisedModel


class FunctionScore(Q.Query):
    name = "function_score"


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
        model: SupervisedModel,
        search_vector: ndarray=None) -> Q.Query:

    if search_vector is None:
        search_vector = model.get_sentence_vector(search_term)
    additional_keywords, similarity = model.get_labels_for_vector(
        search_vector, 10)
    additional_keywords = [k.replace("_", " ")
                           for k in additional_keywords]

    # Insert the original search term
    additional_keywords.insert(0, search_term)

    terms = Q.Terms(**{fields.keywords.name: additional_keywords})

    return terms


def function_score_word_vector_query(
        search_term: str,
        model: SupervisedModel,
        boost_mode: str="replace",
        search_vector: ndarray=None) -> Q.Query:
    from server.search.fields import embedding_vector

    if search_vector is None:
        search_vector = model.get_sentence_vector(search_term)

    script_score = vector_script_score(embedding_vector, search_vector)

    function_score = FunctionScore(
        boost_mode=boost_mode,
        script_score=script_score)
    return function_score


def content_query(search_term, model: SupervisedModel, **kwargs) -> Q.Query:
    from server.search.filter_functions import content_filter_functions
    from server.search.queries import content_query, function_score_content_query

    # Build the original ONS content query
    query = content_query(search_term)

    # Get the search term vector
    search_vector = model.get_sentence_vector(search_term)

    # Build additional keywords query
    terms_query = word_vector_keywords_query(search_term, model, search_vector=search_vector)

    # Combine above into dis_max
    query = Q.DisMax(queries=[query, terms_query])

    # Build function score query
    function_score_query = function_score_word_vector_query(search_term, model, search_vector=search_vector)

    # Return bool query
    bool_query = Q.Bool(must=[query], should=[function_score_query])

    # Apply function scores
    function_scores = kwargs.pop(
        "function_scores", content_filter_functions())

    if function_scores is not None:
        bool_query = function_score_content_query(
            bool_query,
            function_scores)
    return bool_query
