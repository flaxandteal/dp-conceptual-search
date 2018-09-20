"""
This file contains all routes for the /search API
"""
from sanic import Blueprint
from sanic.response import json, HTTPResponse

from server.request import ONSRequest
from server.search.sanic_search_engine import SanicSearchEngine
from ons.search.response.search_result import SearchResult

from ons.search.index import Index
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
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.content_query(request)

    return json(search_result.to_dict(), 200)


@search_blueprint.route('/ons/counts', methods=['GET', 'POST'], strict_slashes=True)
async def ons_counts_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the ONS list type
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.type_counts_query(request)

    return json(search_result.to_dict(), 200)


@search_blueprint.route('/ons/featured', methods=['GET', 'POST'], strict_slashes=True)
async def ons_counts_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the ONS list type
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.featured_result_query(request)

    return json(search_result.to_dict(), 200)
