from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.requests import get_form_param

from server.search import hits_to_json
from server.search.sort_by import SortFields
from server.search.search_engine import get_index, BaseSearchEngine, SearchEngine

from typing import ClassVar

search_blueprint = Blueprint('search', url_prefix='/search')


async def execute_search(request: Request, search_engine_cls: ClassVar, search_term: str, type_filters) -> dict:
    """
    Simple search API to query Elasticsearch
    """
    from server.search.multi_search import AsyncMultiSearch

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
        type_filters=type_filters)

    featured_result_query = search_engine_cls().featured_result_query(search_term)

    # Create multi-search request
    ms = AsyncMultiSearch(using=client, index=get_index())
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


@search_blueprint.route('/ons', methods=["GET", "POST"])
async def search(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine
    :param request:
    :return:
    """
    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(request, "filter", False, None)

        response = await execute_search(request, SearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/data', methods=["GET", "POST"])
async def search_data(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine. Limits type filters for SearchData endpoint.
    :param request:
    :return:
    """
    from server.search.type_filter import filters

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(request, "filter", False, filters["data"])

        response = await execute_search(request, SearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/publications', methods=["GET", "POST"])
async def search_publications(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine. Limits type filters for SearchPublications endpoint.
    :param request:
    :return:
    """
    from server.search.type_filter import filters

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(request, "filter", False, filters["publications"])

        response = await execute_search(request, SearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/departments', methods=["GET", "POST"])
async def search_publications(request: Request):
    """
    Performs the ONS departments query
    :param request:
    :return:
    """
    search_term = request.args.get("q")
    if search_term is not None:
        import inspect

        current_app = request.app

        client = current_app.es_client

        s = SearchEngine(using=client, index="departments")
        response = s.departments_query(search_term).execute()

        if inspect.isawaitable(response):
            response = await response

        result = {
            "numberOfResults": response.hits.total,
            "took": response.took,
            "results": [hit for hit in response.hits.hits]
        }

        return json(result)
    raise InvalidUsage("no query provided")