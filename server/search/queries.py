from . import fields
from elasticsearch_dsl import query as Q


def _get_field_name(field):
    if isinstance(field, fields.Field):
        return field.name
    return field


def match(field, search_term, **kwargs) -> Q.Query:
    field_name = _get_field_name(field)

    query_dict = {
        field_name: {
            "query": search_term,
        }
    }

    for item in kwargs:
        query_dict[field_name][item] = kwargs[item]

    q = Q.Match(**query_dict)
    return q


def multi_match(field_list, search_term, **kwargs) -> Q.Query:
    if hasattr(field_list, "__iter__") is False:
        field_list = [field_list]

    formatted_field_list = []
    for field in field_list:
        field_name = _get_field_name(field)
        formatted_field_list.append(field_name)

    query_dict = {
        "query": search_term,
        "fields": formatted_field_list,
    }

    for item in kwargs:
        query_dict[item] = kwargs[item]

    q = Q.MultiMatch(**query_dict)
    return q


def content_query(search_term) -> Q.DisMax:
    """
    Returns the default ONS content query

    :param search_term:
    :param function_scores:
    :param compute_additional_keywords:
    :return:
    """
    q = Q.DisMax(
        queries=[
            Q.Bool(
                should=[
                    match(fields.title_no_dates, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    match(fields.title_no_stem, search_term, type="boolean", boost=10.0,
                          minimum_should_match="1<-2 3<80% 5<60%"),
                    multi_match([fields.title.field_name_boosted, fields.edition.field_name_boosted], search_term,
                                type="cross_fields", minimum_should_match="3<80% 5<60%")
                ]
            ),
            multi_match([fields.summary.name, fields.metaDescription.name], search_term,
                        type="best_fields", minimum_should_match="75%"),
            match(fields.keywords, search_term, type="boolean", operator="AND"),
            multi_match([fields.cdid.name, fields.datasetId.name], search_term),
            match(fields.searchBoost, search_term, type="boolean", operator="AND", boost=100.0)
        ]
    )

    return q


def function_score_content_query(
        query: Q.Query,
        function_scores: list) -> Q.Query:
    return Q.FunctionScore(query=query, functions=function_scores)


def type_counts_query() -> dict:
    type_count_query = {
        "docCounts": {
            "terms": {
                "field": "_type"
            }
        }
    }

    return type_count_query
