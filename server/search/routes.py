from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.requests import get_form_param

from . import hits_to_json
from .sort_by import SortFields
from .search_engine import get_index

search_blueprint = Blueprint('search', url_prefix='/search')


async def execute_search(request: Request, search_term: str, sort_by: SortFields, **kwargs) -> dict:
    """
    Simple search API to query Elasticsearch
    """
    from server.search.multi_search import AsyncMultiSearch

    # Get the event loop
    current_app = request.app

    # Get the Elasticsearch client
    client = current_app.es_client

    conceptual_search = current_app.config.get("CONCEPTUAL_SEARCH", False)
    if conceptual_search:
        from server.search.conceptual_search.conceptual_search_engine import ConceptualSearchEngine as SearchEngine
    else:
        from server.search.search_engine import SearchEngine

    # Get page_number/size params
    page_number = int(get_form_param(request, "page", False, 1))
    page_size = int(get_form_param(request, "size", False, 10))

    type_counts_query = SearchEngine().type_counts_query(search_term)

    content_query = SearchEngine().content_query(
        search_term,
        sort_by=sort_by,
        current_page=page_number,
        size=page_size,
        **kwargs)

    featured_result_query = SearchEngine().featured_result_query(search_term)

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
        sort_by.name)

    return response


@search_blueprint.route('/ons', methods=["GET", "POST"])
async def search(request: Request):
    """

    :param request:
    :return:
    """
    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(request, "filter", False, None)

        # Get sort_by. Default to relevance
        sort_by_str = get_form_param(request, "sort_by", False, "relevance")
        sort_by = SortFields[sort_by_str]

        # Execute the search
        response = await execute_search(
            request,
            search_term,
            sort_by,
            type_filters=type_filters)
        return json(response)
    raise InvalidUsage("no query provided")
