from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.requests import get_form_param

from server.search import hits_to_json
from server.search.sort_by import SortFields
from server.search.search_engine import get_index, BaseSearchEngine, SearchEngine

search_blueprint = Blueprint('search', url_prefix='/search')


async def execute_search(request: Request, search_engine_cls: type, search_term: str):
    """
    Simple search API to query Elasticsearch
    """
    from server.search.multi_search import AsyncMultiSearch
    from server.search.type_filter import all_filter_funcs

    if not issubclass(search_engine_cls, BaseSearchEngine):
        raise InvalidUsage(
            "expected instance of 'BaseSearchEngine', got %s" %
            search_engine_cls)

    # Get the event loop
    current_app = request.app

    # Get the Elasticsearch client
    client = current_app.es_client

    # Get any content type filters
    type_filters = get_form_param(request, "filter", False, all_filter_funcs())

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


@search_blueprint.route('/ons/conceptual', methods=["GET", "POST"])
async def conceptual_search(request: Request):
    """
    Performs a search request using the new ConceptualSearchEngine
    :param request:
    :return:
    """
    conceptual_search_enabled = request.app.config.get(
        "CONCEPTUAL_SEARCH_ENABLED", False)
    if conceptual_search_enabled:
        from server.search.conceptual_search.conceptual_search_engine import ConceptualSearchEngine

        search_term = request.args.get("q")
        if search_term is not None:
            response = await execute_search(request, ConceptualSearchEngine, search_term)
            return response
        raise InvalidUsage("no query provided")
    raise NotImplementedError("Conceptual search is currently disabled")


@search_blueprint.route('/ons', methods=["GET", "POST"])
async def search(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine
    :param request:
    :return:
    """
    search_term = request.args.get("q")
    if search_term is not None:
        response = await execute_search(request, SearchEngine, search_term)
        return response
    raise InvalidUsage("no query provided")
