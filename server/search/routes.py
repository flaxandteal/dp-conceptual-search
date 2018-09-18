"""
This file contains all routes for the /search API
"""
from sanic import Blueprint
from sanic.response import json, HTTPResponse

from server.request import ONSRequest
from server.search.util import SanicSearchEngine
from ons.search.sort_fields import SortFields
from ons.search.response.search_result import SearchResult

search_blueprint = Blueprint('search', url_prefix='/search')


@search_blueprint.route('/ons/content', methods=['GET', 'POST'], strict_slashes=True)
async def ons_content_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles content queries to the ONS list type
    :param request:
    :return:
    """
    from ons.search.index import Index
    from ons.search.response.ons_response import ONSResponse
    from ons.search.client.search_engine import SearchEngine

    # Initialise the search engine
    engine_factory = SanicSearchEngine(request.get_app(), SearchEngine, Index.ONS)
    engine: SearchEngine = engine_factory.get_search_engine_instance()

    # Perform the query
    search_term = request.get_search_term()
    page = request.get_current_page()
    page_size = request.get_page_size()
    sort_by: SortFields = request.get_sort_by()

    response: ONSResponse = await engine.content_query(search_term, page, page_size, sort_by=sort_by).execute()
    
    search_result: SearchResult = response.to_search_result(page, page_size, sort_by, doc_counts={})

    return json(search_result.to_dict(), 200)
