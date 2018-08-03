from ons.search.type_filter import *

from typing import List


def type_filter_function(type_filter: TypeFilter) -> List[dict]:
    filter_funcs = []
    for content_type in type_filter.content_types:
        filter_funcs.append(content_type_filter_function(content_type))

    return filter_funcs


def content_type_filter_function(content_type) -> dict:
    return {
        "filter": {
            "term": {
                "_type": content_type.name
            },
        },
        "weight": content_type.weight
    }


def content_filter_functions() -> List[dict]:
    """
    Returns filter functions used in a content_query
    :return:
    """
    types = [t for t in content_types if t.weight > 1.0]

    funcs = []

    for content_type in types:
        funcs.append(content_type_filter_function(content_type))
    return funcs
