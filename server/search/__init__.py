from server.requests import get_form_param

from server.search.hit import Hit
from server.search.indices import Index
from server.search.sort_by import SortOrder, SortFields
from server.search.search_engine import BaseSearchEngine
from server.search.paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK
from server.search.sort_by import SortFields
from server.search.multi_search import AsyncMultiSearch
from server.search.search_engine import BaseSearchEngine

from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from typing import ClassVar
from numpy import ndarray


async def execute_search(request: Request, search_engine_cls: ClassVar, search_term: str, type_filters, user_vector: ndarray=None) -> dict:
    """
    Simple search API to query Elasticsearch
    TODO - Modify to prevent building query multiple times
    """
    if not issubclass(search_engine_cls, BaseSearchEngine):
        raise InvalidUsage(
            "expected instance of 'BaseSearchEngine', got %s" %
            search_engine_cls)

    # Get the event loop
    current_app = request.app

    # Get the Elasticsearch client
    client = current_app.es_client

    # Get sort_by. Default to relevance
    sort_by_str = get_form_param(request, "sort_by", False, "relevance")
    sort_by = SortFields[sort_by_str]

    # Get page_number/size params
    page_number = int(get_form_param(request, "page", False, 1))
    page_size = int(get_form_param(request, "size", False, 10))

    type_counts_query = search_engine_cls().type_counts_query(search_term)

    content_query = search_engine_cls().content_query(
        search_term,
        sort_by=sort_by,
        current_page=page_number,
        size=page_size,
        type_filters=type_filters,
        user_vector=user_vector)

    featured_result_query = search_engine_cls().featured_result_query(search_term)

    # Create multi-search request
    ms = AsyncMultiSearch(using=client, index=Index.ONS.value)
    ms = ms.add(type_counts_query)
    ms = ms.add(content_query)
    ms = ms.add(featured_result_query)

    responses = ms.execute()

    # Return the hits as JSON
    response = await hits_to_json(
        responses,
        page_number,
        page_size,
        sort_by=sort_by)

    return json(response)


def buckets_to_json(buckets) -> (dict, int):
    total = 0

    result = {}
    for item in buckets:
        item_key = item["key"]
        count = item["doc_count"]
        result[item_key] = count
        total += count

    return result, total


def get_var(input_dict: dict, accessor_string: str):
    """Gets data from a dictionary using a dotted accessor-string"""
    current_data = input_dict
    for chunk in accessor_string.split('.'):
        current_data = current_data.get(chunk, {})
    return current_data


def _highlight(highlighted_text: str, val: str) -> str:
    val = val.replace(
        highlighted_text,
        "<strong>%s</strong>" % highlighted_text)

    val = val.replace(
        highlighted_text.lower(),
        "<strong>%s</strong>" % highlighted_text.lower())
    return val


def marshall_hits(hits) -> list:
    """
    Substitues highlights into fields and returns valid JSON
    :param hits:
    :return:
    """
    import re

    hits_list = []
    for hit in hits:
        hit_dict = Hit(hit.to_dict())
        if hasattr(hit.meta, "highlight"):
            highlight_dict = hit.meta.highlight.to_dict()
            for highlight_key in highlight_dict:
                for fragment in highlight_dict[highlight_key]:
                    fragment = fragment.strip()
                    if "<strong>" in fragment and "</strong>" in fragment:
                        highlighted_text = " ".join(re.findall(
                            "<strong>(.*?)</strong>", fragment))

                        val = get_var(hit_dict, highlight_key)

                        if isinstance(val, str):
                            hit_dict.set_value(
                                highlight_key, _highlight(
                                    highlighted_text, val))
                        elif hasattr(val, "__iter__"):
                            highlighted_vals = []
                            for v in val:
                                highlighted_vals.append(
                                    _highlight(highlighted_text, v))
                            hit_dict.set_value(highlight_key, highlighted_vals)

        # rename 'type' field to '_type'
        hit_dict["_type"] = hit_dict.pop("type")
        hits_list.append(hit_dict)
    return hits_list


async def hits_to_json(
        responses,
        page_number: int,
        page_size: int,
        sort_by: SortFields=SortFields.relevance) -> dict:
    """
    Replicates the JSON response of Babbage
    :return:
    """
    import inspect

    if inspect.isawaitable(responses):
        responses = await responses

    result = {}
    for search, response in responses:
        assert isinstance(
            search, BaseSearchEngine), "Expected instance of BaseSearchEngine, got %s" % type(search)
        if hasattr(
                response,
                "aggregations") and hasattr(
                response.aggregations,
                "docCounts"):
            aggs = response.aggregations.__dict__["_d_"]["docCounts"]
            buckets = aggs["buckets"]
            if len(buckets) > 0:
                # Type counts query
                aggregations, total_hits = buckets_to_json(buckets)

                result["counts"] = {
                    "numberOfResults": response.hits.total,
                    "docCounts": aggregations
                }
        elif search.query_size == 1:
            # Featured result query
            featured_result_hits = [h.to_dict()
                                    for h in response.hits]

            result["featuredResult"] = {
                "numberOfResults": len(featured_result_hits),
                "results": featured_result_hits
            }
        else:
            # Content query - Init Paginator
            paginator = Paginator(
                response.hits.total,
                MAX_VISIBLE_PAGINATOR_LINK,
                page_number,
                page_size)

            result["result"] = {
                "numberOfResults": response.hits.total,
                "took": response.took,
                "results": marshall_hits(response.hits),
                "docCounts": {},
                "paginator": paginator.to_dict(),
                "sortBy": sort_by.name
            }

    return result
