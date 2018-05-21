from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.requests import get_request_param, get_form_param

from . import hits_to_json
from .sort_by import SortFields
from .search_engine import get_index

search_blueprint = Blueprint('search', url_prefix='/search')


def execute_type_counts_query(
        search_term: str,
        client,
        conceptual_search: bool):
    # Init SearchEngine
    index = get_index()

    if conceptual_search:
        from .conceptual_search.conceptual_search_engine import ConceptualSearchEngine as SearchEngine
    else:
        from .search_engine import SearchEngine
    s = SearchEngine(using=client, index=index)

    # Define type counts (aggregations) query
    s = s.type_counts_query(search_term)

    # Execute
    type_counts_response = s.execute()

    return type_counts_response


def execute_content_query(
        search_term: str,
        sort_by: SortFields,
        page_number: int,
        page_size: int,
        client,
        conceptual_search: bool,
        **kwargs):
    # Init SearchEngine
    index = get_index()

    if conceptual_search:
        from .conceptual_search.conceptual_search_engine import ConceptualSearchEngine as SearchEngine
    else:
        from .search_engine import SearchEngine
    s = SearchEngine(using=client, index=index)

    # Define the query with sort and paginator
    s = s.content_query(
        search_term,
        sort_by=sort_by,
        current_page=page_number,
        size=page_size,
        **kwargs)

    # Execute the query
    content_response = s.execute()

    return content_response


def execute_featured_results_query(
        search_term: str,
        client,
        conceptual_search: bool):
    # Init the SearchEngine
    index = get_index()

    if conceptual_search:
        from .conceptual_search.conceptual_search_engine import ConceptualSearchEngine as SearchEngine
    else:
        from .search_engine import SearchEngine
    s = SearchEngine(using=client, index=index)

    # Define the query
    s = s.featured_result_query(search_term)

    # Execute the query
    featured_result_response = s.execute()

    return featured_result_response


async def execute_search(request: Request, search_term: str, sort_by: SortFields, **kwargs) -> dict:
    """
    Simple search API to query Elasticsearch
    """
    # Get the event loop
    current_app = request.app

    # Get the Elasticsearch client
    client = current_app.es_client

    # Perform the search
    conceptual_search = get_request_param(
        request, "conceptual", False, "true").lower() == "true"

    # Get page_number/size params
    page_number = int(get_form_param(request, "page", False, 1))
    page_size = int(get_form_param(request, "size", False, 10))

    # Execute type counts query
    type_counts_response = execute_type_counts_query(
        search_term, client, conceptual_search)

    # Perform the content query to populate the SERP
    content_response = execute_content_query(
        search_term,
        sort_by,
        page_number,
        page_size,
        client,
        conceptual_search,
        **kwargs)

    featured_result_response = None
    if page_number == 1:
        featured_result_response = execute_featured_results_query(
            search_term, client, conceptual_search)

    # Return the hits as JSON
    response = await hits_to_json(
        content_response,
        type_counts_response,
        page_number,
        page_size,
        sort_by.name,
        featured_result_response=featured_result_response)

    return response


@search_blueprint.route('/ons', methods=["POST"])
async def search(request: Request):
    """
    TODO - Implement MultiSearch API
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
