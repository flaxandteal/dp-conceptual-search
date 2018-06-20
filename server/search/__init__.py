from server.requests import get_form_param

from server.search.utils import hits_to_json
from server.search.sort_by import SortFields
from server.search.indices import Index
from server.search.search_engine import BaseSearchEngine
from server.search.multi_search import AsyncMultiSearch

from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.exceptions import InvalidUsage

from typing import ClassVar
from numpy import ndarray


async def execute_search(request: Request, search_engine_cls: ClassVar, search_term: str, type_filters, user_vector: ndarray=None) -> HTTPResponse:
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
