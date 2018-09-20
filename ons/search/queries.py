"""
Defines a series of useful Elasticsearch queries for the ONS
"""
from typing import List

from elasticsearch_dsl import query as Q
from elasticsearch_dsl.aggs import A as Aggregation

from core.search.query_helper import match, multi_match
from ons.search.content_type import ContentType
from ons.search.fields import Fields


def type_counts_query() -> Aggregation:
    """
    Helper method for generating ONS type counts aggregation
    :return:
    """
    return Aggregation("terms", field=Fields.TYPE.value.name)


def departments_query(search_term: str) -> Q.Query:
    """
    Returns the ONS departments query
    :param search_term:
    :return:
    """
    return Q.Match(**{"terms": {"query": search_term, "type": "boolean"}})


def content_query(search_term: str, **kwargs) -> Q.DisMax:
    """
    Returns the default ONS content query

    :param search_term:
    :return:
    """
    q = Q.DisMax(
        queries=[
            Q.Bool(
                should=[
                    match(Fields.TITLE_NO_DATES.value.name, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    match(Fields.TITLE_NO_STEM.value.name, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    multi_match([Fields.TITLE.value.field_name_boosted, Fields.EDITION.value.field_name_boosted], search_term,
                                type="cross_fields", minimum_should_match="3<80% 5<60%")
                ]
            ),
            multi_match([Fields.SUMMARY.value.name, Fields.META_DESCRIPTION.value.name], search_term,
                        type="best_fields", minimum_should_match="75%"),
            match(Fields.KEYWORDS.value.name, search_term, type="boolean", operator="AND"),
            multi_match([Fields.CDID.value.name, Fields.DATASET_ID.value.name], search_term),
            match(Fields.SEARCH_BOOST.value.name, search_term, type="boolean", operator="AND", boost=100.0)
        ],
        **kwargs
    )

    return q


def function_score_content_query(query: Q.Query, content_types: List[ContentType], boost: float=1.0) -> Q.Query:
    """
    Generate a function score query using ContentType weights
    :param query:
    :param content_types:
    :param boost:
    :return:
    """
    function_scores = []
    for content_type in content_types:
        function_scores.append(content_type.filter_function())

    return Q.FunctionScore(query=query, functions=function_scores, boost=boost)
