from sanic import Blueprint
from sanic.exceptions import InvalidUsage

from ..response import json

from . import hits_to_json
from .sort_by import SortFields
from .search_engine import SearchEngine, get_client, get_index
from ..requests import get_form_param

search_blueprint = Blueprint('search', url_prefix='/search')


async def execute_type_counts_query(search_term, client):
    # Init SearchEngine
    index = get_index()
    s = SearchEngine(using=client, index=index)

    # Define type counts (aggregations) query
    s = s.type_counts_query(search_term)

    # Execute
    type_counts_response = await s.execute()

    return type_counts_response


async def execute_content_query(search_term, sort_by, page_number, page_size, client, **kwargs):
    # Init SearchEngine
    index = get_index()
    s = SearchEngine(using=client, index=index)

    # Define the query with sort and paginator
    s = s.content_query(
        search_term, sort_by=sort_by, current_page=page_number, size=page_size, **kwargs)

    # Execute the query
    content_response = await s.execute()

    return content_response


async def execute_featured_results_query(search_term, client):
    # Init the SearchEngine
    index = get_index()
    s = SearchEngine(using=client, index=index)

    # Define the query
    s = s.featured_result_query(search_term)

    # Execute the query
    featured_result_response = await s.execute()

    return featured_result_response


async def execute_search(request, search_term, sort_by, **kwargs):
    """
    Simple search API to query Elasticsearch
    """
    # Get the event loop
    current_app = request.app

    # Get the Elasticsearch client
    client = get_client(loop=current_app.loop)

    # Perform the search

    # Get page_number/size params
    page_number = int(get_form_param(request, "page", False, 1))
    page_size = int(get_form_param(request, "size", False, 10))

    # Execute type counts query
    type_counts_response = execute_type_counts_query(search_term, client)

    # Perform the content query to populate the SERP
    content_response = execute_content_query(search_term, sort_by, page_number, page_size, client, **kwargs)

    featured_result_response = None
    if page_number == 1:
        featured_result_response = await execute_featured_results_query(search_term, client)

    # Return the hits as JSON
    return hits_to_json(
        await content_response,
        await type_counts_response,
        page_number,
        page_size,
        sort_by.name,
        featured_result_response=featured_result_response)


@search_blueprint.route('/ons', methods=["POST"])
async def search(request):
    from datetime import datetime

    start = datetime.now()
    search_term = request.args.get("q", None)
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

        end = datetime.now()
        print("Duration: {}".format(end-start))

        return json(response)
    raise InvalidUsage("no query provided")
