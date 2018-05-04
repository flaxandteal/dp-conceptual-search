from sanic import Blueprint
from sanic.exceptions import InvalidUsage

from ..response import json

from . import hits_to_json, aggs_to_json
from .paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK
from .sort_by import SortFields
from .search_engine import SearchEngine, get_client, get_index
from ..requests import get_form_param

search_blueprint = Blueprint('search', url_prefix='/search')


def execute_search(request, search_term, sort_by, **kwargs):
    """
    Simple search API to query Elasticsearch
    """
    # Get the Elasticsearch client
    client = get_client()

    # Perform the search
    ons_index = get_index()

    # Init SearchEngine
    s = SearchEngine(using=client, index=ons_index)

    # Define type counts (aggregations) query
    s = s.type_counts_query(search_term)

    # Execute
    type_counts_response = s.execute()

    # Format the output
    aggregations, total_hits = aggs_to_json(
        type_counts_response.aggregations, "docCounts")

    # Setup initial paginator
    page_number = int(get_form_param(request, "page", False, 1))
    page_size = int(get_form_param(request, "size", False, 10))

    paginator = None
    if total_hits > 0:
        paginator = Paginator(
            total_hits,
            MAX_VISIBLE_PAGINATOR_LINK,
            page_number,
            page_size)

    # Perform the content query to populate the SERP

    # Init SearchEngine
    s = SearchEngine(using=client, index=ons_index)

    # Define the query with sort and paginator
    s = s.content_query(
        search_term, sort_by=sort_by, paginator=paginator, **kwargs)

    # Execute the query
    content_response = s.execute()

    # Update the paginator
    paginator = Paginator(
        content_response.hits.total,
        MAX_VISIBLE_PAGINATOR_LINK,
        page_number,
        page_size)

    # Check for featured results
    featured_result_response = None
    # Only do this if we have results and are on the first page
    if total_hits > 0 and paginator.current_page <= 1:
        # Init the SearchEngine
        s = SearchEngine(using=client, index=ons_index)

        # Define the query
        s = s.featured_result_query(search_term)

        # Execute the query
        featured_result_response = s.execute()

    # Return the hits as JSON
    return hits_to_json(
        content_response,
        aggregations,
        paginator,
        sort_by.name,
        featured_result_response=featured_result_response)


@search_blueprint.route('/ons', methods=["POST"])
async def search(request):
    search_term = request.args.get("q", None)
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(request, "filter", False, None)

        # Get sort_by. Default to relevance
        sort_by_str = get_form_param(request, "sort_by", False, "relevance")
        sort_by = SortFields[sort_by_str]

        # Execute the search
        response = execute_search(
            request,
            search_term,
            sort_by,
            type_filters=type_filters)

        return json(response)
    raise InvalidUsage("no query provided")
