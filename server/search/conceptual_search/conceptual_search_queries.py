from elasticsearch_dsl import query as Q

from enum import Enum
from numpy import ndarray

from server.search import fields
from server.word_embedding.supervised_models import SupervisedModel


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


def vector_script_score(
        field: fields.Field,
        vector: ndarray,
        weight: int=1) -> Q.Query:
    params = {
        "cosine": True,
        "field": field.name,
        "vector": vector.tolist()
    }
    script_score = {
        "lang": ScriptLanguage.KNN.value,
        "params": params,
        "script": Scripts.BINARY_VECTOR_SCORE.value,
        "weight": weight
    }

    # return script_score
    return ScriptScore(**script_score)


def date_decay_function() -> Q.Query:
    q = Q.SF('gauss', **{fields.releaseDate.name: {
        "origin": "now",
        "scale": "365d",
        "offset": "30d",
        "decay": 0.5
    }})
    return q


def word_vector_keywords_query(
        search_term: str,
        model: SupervisedModel,
        k: int=10,
        threshold: float=0.1) -> Q.Query:
    """
    TODO - Replace below with call to predict
    TODO - (Re)Index normalised vectors
    :param search_term:
    :param model:
    :param k:
    :param threshold:
    :return:
    """
    labels, probabilities = model.predict(
        search_term, k=k, threshold=threshold)

    match_queries = []
    for label, probability in zip(labels, probabilities):
        match_queries.append(Q.Match(
            **{fields.keywords.name: {"query": label.replace("_", " "), "boost": probability}}))

    # query = Q.DisMax(queries=match_queries)
    query = Q.Bool(should=match_queries)
    return query


def content_query(
        search_term: str,
        model: SupervisedModel,
        boost_mode: BoostMode=BoostMode.AVG,
        min_score: float=0.1,
        **kwargs) -> Q.Query:
    """
    Conceptual search (main) content query.
    Requires embedding_vectors to be indexed in Elasticsearch.
    TODO - Grab current user ID and add as additional vector script score
    :param search_term:
    :param model:
    :param boost_mode:
    :param min_score:
    :return:
    """
    from server.search.fields import embedding_vector
    from server.search.filter_functions import content_filter_functions
    from server.search.queries import content_query as ons_content_query

    search_vector = model.get_sentence_vector(search_term)

    script_score = vector_script_score(embedding_vector, search_vector)
    date_function = date_decay_function()

    function_scores = [script_score.to_dict(), date_function.to_dict()]

    # Build the original ONS content query
    dis_max_query = ons_content_query(search_term)

    # # Build additional keywords query
    terms_query = word_vector_keywords_query(
        search_term, model)

    should = [dis_max_query, terms_query]

    # If user is specified, add a user vector function score
    if 'user_vector' in kwargs:
        user_vector = kwargs.get('user_vector')

        if user_vector is not None:
            assert isinstance(
                user_vector, ndarray), "Must supply user_vector as ndarray"

            # TODO - Test as rescore query
            user_script_score = vector_script_score(
                embedding_vector, user_vector)
            function_scores.append(user_script_score.to_dict())

    additional_function_scores = kwargs.get(
        "function_scores", content_filter_functions())

    if additional_function_scores is not None:
        if hasattr(additional_function_scores, "__iter__") is False:
            additional_function_scores = [additional_function_scores]
        function_scores.extend(additional_function_scores)

    function_score = FunctionScore(
        query=Q.Bool(should=should),
        min_score=min_score,
        boost_mode=boost_mode.value,
        functions=function_scores)

    return function_score
