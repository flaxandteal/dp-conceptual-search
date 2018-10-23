from typing import List

from elasticsearch_dsl import query as Q

from search.queries import ScriptScore


def match_by_uri(uri: str) -> Q.Query:
    """
    Match a document by its uri
    :param uri:
    :return:
    """
    if not uri.startswith("/"):
        uri = "/" + uri
    return Q.Match(_id=uri)


def match(field: str, search_term: str, **kwargs) -> Q.Query:
    """
    Helper method for generating a match query
    :param field:
    :param search_term:
    :param kwargs:
    :return:
    """
    query_dict = {
        field: {
            "query": search_term,
        }
    }

    for item in kwargs:
        query_dict[field][item] = kwargs[item]

    q = Q.Match(**query_dict)
    return q


def multi_match(field_list: List[str], search_term: str, **kwargs) -> Q.Query:
    """
    Helper method for generating a multi-match query
    :param field_list:
    :param search_term:
    :param kwargs:
    :return:
    """
    if hasattr(field_list, "__iter__") is False:
        field_list = [field_list]

    formatted_field_list = []
    for field in field_list:
        formatted_field_list.append(field)

    query_dict = {
        "query": search_term,
        "fields": formatted_field_list,
    }

    for item in kwargs:
        query_dict[item] = kwargs[item]

    q = Q.MultiMatch(**query_dict)
    return q


def boost_score(boost_factor=1.0) -> ScriptScore:
    return ScriptScore(
        script="_score * boostFactor",
        params={
            "boostFactor": boost_factor
        }
    )
