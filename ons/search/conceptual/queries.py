from elasticsearch_dsl import query as Q

from numpy import ndarray

from ons.search import fields
from ons.search.query_dsl import *

from core.word_embedding.models.supervised import SupervisedModel


def vector_script_score(
        field: fields.Field,
        vector: ndarray,
        weight: float = 1.0) -> Q.Query:

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

    if weight > 1:
        script_score['weight'] = weight

    return ScriptScore(**script_score)


def date_decay_function(
        fn: str = "exp",
        origin: str = "now",
        scale: str = "365d",
        offset: str = "30d",
        decay: float = 0.5) -> Q.Query:

    q = Q.SF(fn, **{fields.releaseDate.name: {
        "origin": origin,
        "scale": scale,
        "offset": offset,
        "decay": decay
    }})

    return q


def word_vector_keywords(
        search_term: str,
        model: SupervisedModel,
        k: int = 10,
        threshold: float = 0.1) -> Q.Query:
    """
    :param search_term:
    :param model:
    :param k:
    :param threshold:
    :return:
    """
    labels, probabilities = model.predict_and_format(
        search_term, k=k, threshold=threshold)
    labels.append(search_term)

    return labels, probabilities


def word_vector_keywords_query(
        search_term: str,
        model: SupervisedModel,
        k: int = 10,
        threshold: float = 0.1) -> Q.Query:
    """
    :param search_term:
    :param model:
    :param k:
    :param threshold:
    :return:
    """
    labels, probabilities = word_vector_keywords(search_term, model, k=k, threshold=threshold)

    match_queries = []
    for label, probability in zip(labels, probabilities):
        # match_queries.append(Q.Match(
        #     **{fields.keywords.name: {"query": label, "boost": probability}}))
        match_queries.append(Q.Match(
            **{fields.keywords_raw.name: {"query": label}}))

    query = Q.Bool(should=match_queries)
    return query


def user_rescore_query(
        user_vector: ndarray,
        score_mode: BoostMode = BoostMode.AVG,
        window_size: int = 100,
        query_weight: float = 1.0,
        rescore_query_weight: float = 1.0) -> RescoreQuery:
    """
    Generates a rescore query from a users session vector
    :param user_vector:
    :param score_mode:
    :param window_size:
    :param query_weight:
    :param rescore_query_weight:
    :return:
    """
    user_script_score = vector_script_score(
        fields.embedding_vector, user_vector)

    rescore = {
        "window_size": window_size,
        "query": {
            "score_mode": score_mode.value,
            "rescore_query": {
                "function_score": user_script_score.to_dict()
            },
            "query_weight": query_weight,
            "rescore_query_weight": rescore_query_weight
        }
    }

    return RescoreQuery(**rescore)


def content_query(
        search_term: str,
        model: SupervisedModel,
        **kwargs) -> Q.Query:
    """
    Conceptual search (main) content query.
    Requires embedding_vectors to be indexed in Elasticsearch.
    :param search_term:
    :param model:
    :return:
    """
    from sanic.log import logger
    from core.word_embedding.utils import clean_string

    from ons.search.queries import boost_score
    from ons.search.queries import content_query as ons_content_query
    from ons.search.filter_functions import content_filter_functions

    # Prepare the search term for keyword generation
    clean_search_term = clean_string(search_term)
    search_vector = model.get_sentence_vector(clean_search_term)

    # Build function scores
    script_score = vector_script_score(fields.embedding_vector, search_vector)

    try:
        # Try to build additional keywords query
        terms_query = FunctionScore(
            query=word_vector_keywords_query(clean_search_term, model),
            functions=[script_score.to_dict(), boost_score(0.5).to_dict()],
            boost_mode=BoostMode.REPLACE.value
        )

        logger.info("Generated additional keywords for query '%s': %s" % (
            search_term, terms_query))

        # Build the original content query
        dis_max_query = ons_content_query(search_term)

        # Add content type function scores if specified
        content_function_scores = kwargs.get(
            "function_scores", content_filter_functions())

        if content_function_scores is None:
            content_function_scores = content_filter_functions()
        if hasattr(content_function_scores, "__iter__") is False:
            content_function_scores = [content_function_scores]

        content_function_scores.append(boost_score(100.0).to_dict())

        query = FunctionScore(
            query=dis_max_query,
            functions=content_function_scores
        )

        terms_query = FunctionScore(
            query=terms_query,
            functions=[script_score.to_dict()],
            boost_mode=BoostMode.REPLACE.value
        )

        query = Q.DisMax(
            queries=[query, terms_query]
        )

        return query

    except ValueError as e:
        # Log the error but continue with the query (we can still return results, just can't
        # auto generate keywords for matching.
        # Note the script score will still facilitate non-keyword matching.
        logger.error(
            "Caught exception while generating model keywords: %s",
            str(e),
            exc_info=1)


def recommended_content_query(
        page_uri: str,
        decoded_doc_vector: ndarray,
        user_vector: ndarray = None):
    """
    Query for recommended content using a page embedding vector and an (optional) user vector.
    :return:
    """
    from collections import OrderedDict

    from core.word_embedding.utils import clean_string

    from ons.search.queries import match_by_uri
    from ons.search.fields import embedding_vector

    from server.word_embedding.sanic_word2vec import Models, UnsupervisedModel
    from server.word_embedding.sanic_word2vec import load_model as load_unsup_model
    from server.word_embedding.sanic_supervised_models import SupervisedModels, SupervisedModel
    from server.word_embedding.sanic_supervised_models import load_model as load_sup_model

    # Build the function scores list
    doc_query = vector_script_score(embedding_vector, decoded_doc_vector)
    function_scores = [doc_query.to_dict()]

    # Finally, get similar terms to this vector for a terms query
    # Get a reference to the models
    unsupervised_model: UnsupervisedModel = load_unsup_model(Models.ONS)
    supervised_model: SupervisedModel = load_sup_model(SupervisedModels.ONS)

    similar_by_vector = unsupervised_model.similar_by_vector(
        decoded_doc_vector, ret_sim=False)

    if user_vector is not None:
        # Build the user query
        user_query = vector_script_score(embedding_vector, user_vector)

        # Add to the function scores
        function_scores.append(user_query.to_dict())

        # Get similar words
        similar_by_vector.extend(
            unsupervised_model.similar_by_vector(
                user_vector, ret_sim=False))

    # Remove duplicate terms from similar_by_vector and build sentence
    sentence = " ".join(list(OrderedDict.fromkeys(similar_by_vector)))
    clean_sentence = clean_string(sentence)

    # Build the keywords query from this sentence
    keywords_query = word_vector_keywords_query(
        clean_sentence, supervised_model)

    # Explicitly exclude current page_uri
    query = Q.Bool(must_not=[match_by_uri(page_uri)], should=[keywords_query])

    # Build the function score query
    function_score_query = FunctionScore(
        query=query,
        functions=function_scores,
        boost_mode=BoostMode.AVG.value)

    return function_score_query
