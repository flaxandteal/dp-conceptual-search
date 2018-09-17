"""
Defines a series of useful Elasticsearch queries for the ONS
"""
from elasticsearch_dsl import query as Q
from elasticsearch_dsl.aggs import A as Aggregation

from core.search.query_helper import match, multi_match


def type_counts_query() -> Aggregation:
    """
    Helper method for generating ONS type counts aggregation
    :return:
    """
    from ons.search.fields import _type as type_field
    return Aggregation("terms", field=type_field.name)


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
    from ons.search import fields
    q = Q.DisMax(
        queries=[
            Q.Bool(
                should=[
                    match(fields.title_no_dates.name, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    match(fields.title_no_stem.name, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    multi_match([fields.title.field_name_boosted, fields.edition.field_name_boosted], search_term,
                                type="cross_fields", minimum_should_match="3<80% 5<60%")
                ]
            ),
            multi_match([fields.summary.name, fields.metaDescription.name], search_term,
                        type="best_fields", minimum_should_match="75%"),
            match(fields.keywords.name, search_term, type="boolean", operator="AND"),
            multi_match([fields.cdid.name, fields.datasetId.name], search_term),
            match(fields.searchBoost.name, search_term, type="boolean", operator="AND", boost=100.0)
        ],
        **kwargs
    )

    return q


def function_score_content_query(query: Q.Query, function_scores: list, boost: float=1.0) -> Q.Query:
    return Q.FunctionScore(query=query, functions=function_scores, boost=boost)
