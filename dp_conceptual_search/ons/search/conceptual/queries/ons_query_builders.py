"""
This file contains queries for conceptual search
"""
import logging

from numpy import ndarray
from elasticsearch_dsl import query as Q

from dp_conceptual_search.search.boost_mode import BoostMode
from dp_conceptual_search.ons.search.queries import ons_query_builders
from dp_conceptual_search.search.dsl.function_score import FunctionScore
from dp_conceptual_search.ons.search.fields import AvailableFields, Field
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore
from dp_conceptual_search.ons.search.exceptions import MalformedSearchTerm, UnknownSearchVector
from dp_conceptual_search.ons.search.conceptual.client.fasttext_client import get_fasttext_client

from dp_fasttext.client import Client
from dp_fasttext.ml.utils import clean_string, replace_nouns_with_singulars


def word_vector_keywords_query(search_term: str, num_labels: int, threshold: float, client: Client) -> Q.Query:
    """
    Build a bool query to match against generated keyword labels
    :param search_term:
    :param num_labels:
    :param threshold:
    :param client:
    :return:
    """
    # Use the raw keywords field for matching
    field: Field = AvailableFields.KEYWORDS_RAW.value

    # Get predicted labels and their probabilities
    labels, probabilities = client.predict(search_term, num_labels, threshold)

    logging.debug("Generated additional keywords", extra={
        "search_term": search_term,
        "keywords": labels
    })

    # Build the individual match queries
    match_queries = [Q.Match(**{field.name: {"query": label}}) for label in labels]
    return Q.Bool(should=match_queries)


def content_query(search_term: str,
                  field: Field=AvailableFields.EMBEDDING_VECTOR.value,
                  num_labels: int=10,
                  threshold: float=0.1) -> Q.Query:
    """
    Defines the ONS conceptual search content query
    :param search_term:
    :param field:
    :param num_labels:
    :param threshold:
    :return:
    """
    # Initialise dp-fastText client
    client: Client = get_fasttext_client()

    # First, clean the search term and replace all nouns with singulars
    clean_search_term = replace_nouns_with_singulars(clean_string(search_term))

    if len(clean_search_term) == 0:
        raise MalformedSearchTerm(search_term)

    search_vector: ndarray = client.get_sentence_vector(clean_search_term)
    if search_vector is None:
        raise UnknownSearchVector(search_term)

    # Build function scores
    script_score = VectorScriptScore(field.name, search_vector, cosine=True)
    script_score_dict = script_score.to_dict()

    # Generate additional keywords query
    additional_keywords_query = FunctionScore(
        query=word_vector_keywords_query(clean_search_term, num_labels, threshold, client),
        functions=[script_score_dict],
        boost_mode=BoostMode.REPLACE.value
    )

    # Build the original content query
    dis_max_query = ons_query_builders.content_query(search_term)

    # Combine as DisMax with FunctionScore
    query = Q.DisMax(
        queries=[dis_max_query, additional_keywords_query]
    )

    return FunctionScore(
        query=query,
        functions=[script_score_dict],
        boost_mode=BoostMode.AVG.value
    )
