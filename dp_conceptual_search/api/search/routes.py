"""
This file contains all routes for the /search API
"""
from sanic import Blueprint
from sanic.response import HTTPResponse

from dp_conceptual_search.api.response import json
from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.api.search.sanic_search_engine import SanicSearchEngine

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.response.search_result import SearchResult

search_blueprint = Blueprint('search', url_prefix='/search')


@search_blueprint.route('/departments', methods=['GET'], strict_slashes=True)
async def ons_departments_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles departments queries to the ONS list type. Note, filtering by list_type does not apply
    to the featured result (hence we only offer an 'ONS' list type for this API).
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.DEPARTMENTS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.departments_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/content', methods=['GET', 'POST'], strict_slashes=True)
async def ons_content_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles content queries to the <list_type> API.
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.content_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/counts', methods=['GET', 'POST'], strict_slashes=True)
async def ons_counts_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the <list_type> API.
    :param request:
    :param list_type: Not used for type counts query, but allows route to support multiply list_type queries
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.type_counts_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/featured', methods=['GET'], strict_slashes=True)
async def ons_featured_result_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the ONS list type. Note, filtering by list_type does not apply
    to the featured result (hence we only offer an 'ons' list type for this API)
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.featured_result_query(request)

    return json(request, search_result.to_dict(), 200)
