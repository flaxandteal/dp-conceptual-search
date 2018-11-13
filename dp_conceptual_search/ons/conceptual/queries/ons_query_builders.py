"""
This file contains queries for conceptual search
"""
from typing import List
from numpy import ndarray
from elasticsearch_dsl import query as Q

from dp_conceptual_search.search.boost_mode import BoostMode
from dp_conceptual_search.ons.search.queries import ons_query_builders
from dp_conceptual_search.search.dsl.function_score import FunctionScore
from dp_conceptual_search.ons.search.fields import AvailableFields, Field
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore


def word_vector_keywords_query(labels: List[str]) -> Q.Query:
    """
    Build a bool query to match against generated keyword labels
    :param labels:
    :return:
    """
    # Use the raw keywords field for matching
    field: Field = AvailableFields.KEYWORDS_RAW.value

    # Build the individual match queries
    match_queries = [Q.Match(**{field.name: {"query": label}}) for label in labels]

    return Q.Bool(should=match_queries)


def build_content_query(search_term: str, labels: List[str], search_vector: ndarray,
                        field: Field = AvailableFields.EMBEDDING_VECTOR.value) -> Q.Query:
    """
    Defines the ONS conceptual search content query
    :param search_term:
    :param labels:
    :param search_vector:
    :param field:
    :return:
    """
    wv_keywords_query = word_vector_keywords_query(labels)

    # Build function scores
    script_score = VectorScriptScore(field.name, search_vector, cosine=True)
    script_score_dict = script_score.to_dict()

    # Generate additional keywords query
    additional_keywords_query = FunctionScore(
        query=wv_keywords_query,
        functions=[script_score_dict],
        boost_mode=BoostMode.REPLACE.value
    )

    # Build the original content query
    dis_max_query = ons_query_builders.build_content_query(search_term)

    # Combine as DisMax with FunctionScore
    query = Q.DisMax(
        queries=[dis_max_query, additional_keywords_query]
    )

    return FunctionScore(
        query=query,
        functions=[script_score_dict],
        boost_mode=BoostMode.AVG.value
    )
