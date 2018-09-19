"""
This file contains all routes for the /search API
"""
from sanic import Blueprint
from sanic.log import logger
from sanic.response import json, HTTPResponse

from elasticsearch.exceptions import ConnectionError

from server.request import ONSRequest
from server.search.sanic_search_engine import SanicSearchEngine
from ons.search.sort_fields import SortFields
from ons.search.response.search_result import SearchResult

from ons.search.index import Index
from ons.search.response.ons_response import ONSResponse
from ons.search.client.search_engine import SearchEngine

search_blueprint = Blueprint('search', url_prefix='/search')


@search_blueprint.route('/ons/content', methods=['GET', 'POST'], strict_slashes=True)
async def ons_content_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles content queries to the ONS list type
    :param request:
    :return:
    """
    # Initialise the search engine
    engine_factory = SanicSearchEngine(request.get_app(), SearchEngine, Index.ONS)
    engine: SearchEngine = engine_factory.get_search_engine_instance()

    # Perform the query
    search_term = request.get_search_term()
    page = request.get_current_page()
    page_size = request.get_page_size()
    sort_by: SortFields = request.get_sort_by()

    try:
        response: ONSResponse = await engine.content_query(search_term, page, page_size, sort_by=sort_by).execute()
    except ConnectionError as e:
        message = "Unable to connect to Elasticsearch cluster to perform content query request"
        logger.error(message, exc_info=e)
        return json(message, 500)

    search_result: SearchResult = response.to_content_query_search_result(page, page_size, sort_by)

    return json(search_result.to_dict(), 200)


@search_blueprint.route('/ons/counts', methods=['GET', 'POST'], strict_slashes=True)
async def ons_counts_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the ONS list type
    :param request:
    :return:
    """
    # Initialise the search engine
    engine_factory = SanicSearchEngine(request.get_app(), SearchEngine, Index.ONS)
    engine: SearchEngine = engine_factory.get_search_engine_instance()

    # Perform the query
    search_term = request.get_search_term()

    try:
        response: ONSResponse = await engine.type_counts_query(search_term).execute()
    except ConnectionError as e:
        message = "Unable to connect to Elasticsearch cluster to perform type counts query request"
        logger.error(message, exc_info=e)
        return json(message, 500)

    search_result: SearchResult = response.to_type_counts_query_search_result()

    return json(search_result.to_dict(), 200)
