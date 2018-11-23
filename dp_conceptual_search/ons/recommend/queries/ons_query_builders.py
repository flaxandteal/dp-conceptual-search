"""
This file contains methods to build recommendation queries
"""
from typing import List
from elasticsearch_dsl import query as Q

from dp_conceptual_search.search.boost_mode import BoostMode
from dp_conceptual_search.search.query_helper import match_by_uri
from dp_conceptual_search.search.dsl.function_score import FunctionScore
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.conceptual.queries.ons_query_builders import word_vector_keywords_query


def similar_to_uri(uri: str, labels: List[str], vector_script_score: VectorScriptScore) -> Q.Query:
    """
    Builds a query to find similar content to (but excluding) the given uri
    :return:
    """
    # First, build a uri match query
    match_query: Q.Query = match_by_uri(uri)

    # Build keywords query
    wv_keywords_query = word_vector_keywords_query(labels)
    vector_script_score_dict = vector_script_score.to_dict()

    # Generate additional keywords query
    additional_keywords_query = FunctionScore(
        query=wv_keywords_query,
        functions=[vector_script_score_dict],
        boost_mode=BoostMode.REPLACE.value
    )

    # Combine into bool query and explicitly omit the current page with must_not clause
    query: Q.Bool = Q.Bool(must_not=[match_query], should=[additional_keywords_query])

    # Convert to function score
    query: FunctionScore = FunctionScore(
        query=query,
        functions=[vector_script_score_dict],
        boost_mode=BoostMode.AVG.value
    )

    return query
