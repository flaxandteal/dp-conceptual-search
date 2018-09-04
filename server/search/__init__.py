from sanic.request import Request
from sanic.response import HTTPResponse

from ons.search.response import ONSResponse
from ons.search.sort_fields import SortFields
from ons.search.search_engine import AbstractSearchClient

from server.search.list_type import ListType

from typing import ClassVar

available_list_types = ['ons', 'onsdata', 'onspublications']


async def _await_response(response) -> ONSResponse:
    """
    Util method for checking if an Elasticsearch response is awaitable (and await if true)
    :param response:
    :return:
    """
    from inspect import isawaitable

    if isawaitable(response):
        response = await response

    return response


async def search_with_client(request: Request, list_type: ListType, endpoint: str,
                             search_engine_cls: ClassVar[AbstractSearchClient], **kwargs: dict):
    """
    Builds the search engine client from the specified class
    :param request:
    :param list_type:
    :param endpoint:
    :param search_engine_cls:
    :return:
    """
    from sanic import Sanic

    from ons.search.indicies import Index

    from server.search.endpoint import available_endpoints, Endpoint

    if issubclass(search_engine_cls, AbstractSearchClient):
        if endpoint in available_endpoints:
            app: Sanic = request.app
            es_client = app.es_client

            # Departments or ONS index?
            index: Index = Index.DEPARTMENTS if endpoint == Endpoint.DEPARTMENTS.value else Index.ONS

            # Build the search engine client
            s: AbstractSearchClient = search_engine_cls(
                using=es_client,
                index=index.value
            )

            # Execute the query
            return await execute(request, s, list_type, endpoint, **kwargs)
        else:
            from sanic.exceptions import NotFound
            raise NotFound("No route for list_type/endpoint: '%s/%s'" % (list_type, endpoint))
    else:
        from sanic.exceptions import InvalidUsage
        raise InvalidUsage("Class '%s' is not a subclass of AbstractSearchClient" % search_engine_cls)


async def execute(request: Request, search_engine: AbstractSearchClient, list_type: ListType, endpoint: str,
                  **kwargs: dict) -> HTTPResponse:
    """
    Executes an ONS search query using the provided client for the given list type (ons, onsdata or onspublications)
    and endpoint (content, type counts, featured or departments).
    :param request:
    :param search_engine:
    :param list_type:
    :param endpoint:
    :param kwargs:
    :return:
    """
    from sanic.response import json as json_response

    from server.search.endpoint import available_endpoints, Endpoint
    from server.requests import get_json_param, extract_page, extract_page_size

    if endpoint not in available_endpoints:
        from sanic.exceptions import NotFound
        raise NotFound("No route for list_type/endpoint: '%s/%s'" % (list_type, endpoint))

    search_term = request.args.get("q", None)
    result: dict = None

    # Get sort_by. Default to relevance
    sort_by_str = get_json_param(request, "sort_by", False, "relevance")
    sort_by = SortFields[sort_by_str]

    # Get page_number/size params
    page_number: int = extract_page(request)
    page_size: int = extract_page_size(request)

    if search_term is not None:
        if endpoint == Endpoint.CONTENT.value:
            from server.search.utils import get_type_filters

            # Get any content type filters
            type_filters = get_type_filters(request, list_type)

            params = {**{'type_filters': type_filters, 'sort_by': sort_by}, **kwargs}

            search_engine: AbstractSearchClient = search_engine.content_query(
                search_term,
                page_number,
                page_size,
                **params
            )

            response: ONSResponse = await _await_response(search_engine.execute())
            result = response.response_to_json(page_number, page_size, sort_by)

        elif endpoint == Endpoint.TYPE_COUNTS.value:
            from ons.search.type_filter import default_filters

            search_engine: AbstractSearchClient = search_engine.type_counts_query(
                search_term,
                type_filters=default_filters(),
                **kwargs
            )

            response: ONSResponse = await _await_response(search_engine.execute())
            result = response.aggs_to_json()

        elif endpoint == Endpoint.FEATURED.value:
            search_engine: AbstractSearchClient = search_engine.featured_result_query(search_term)

            response: ONSResponse = await _await_response(search_engine.execute())
            result = response.featured_result_to_json()

        elif endpoint == Endpoint.DEPARTMENTS.value:
            search_engine: AbstractSearchClient = search_engine.departments_query(
                search_term,
                page_number,
                page_size
            )

            response: ONSResponse = await _await_response(search_engine.execute())
            result = response.response_to_json(page_number, page_size, sort_by)

        return json_response(result, 200)

    else:
        from sanic.exceptions import InvalidUsage
        raise InvalidUsage("No query specified for list_type/endpoint: '%s/%s'" % (list_type, endpoint))
