"""
This file contains all routes for the /search API
"""
from sanic import Blueprint
from sanic.response import HTTPResponse

from api.log import logger
from api.response import json
from api.request import ONSRequest
from api.search.list_type import ListType
from api.search.sanic_search_engine import SanicSearchEngine

from ons.search.index import Index
from ons.search.client.search_engine import SearchEngine
from ons.search.response.search_result import SearchResult

search_blueprint = Blueprint('search', url_prefix='/search')


@search_blueprint.route('/', methods=['POST'], strict_slashes=True)
async def proxy_query(request: ONSRequest) -> HTTPResponse:
    """
    Proxy an Elasticsearch query through the APP over HTTP.
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.proxy(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/ons/departments', methods=['GET', 'POST'], strict_slashes=True)
async def ons_departments_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles departments queries to the ONS list type. Note, filtering by list_type does not apply
    to the featured result (hence we only offer an 'ONS' list type for this API).
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.departments_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/<list_type>/content', methods=['GET', 'POST'], strict_slashes=True)
async def ons_content_query(request: ONSRequest, list_type: str) -> HTTPResponse:
    """
    Handles content queries to the <list_type> API.
    :param request:
    :param list_type: The list_type to query against (i.e ons, onsdata or onspublications; see api.search.list_type.py)
    :return:
    """
    # Parse list_type to enum
    if ListType.is_list_type(list_type):
        list_type_enum: ListType = ListType.from_str(list_type)
        # Initialise the search engine
        sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

        # Perform the request
        search_result: SearchResult = await sanic_search_engine.content_query(request, list_type_enum)

        return json(request, search_result.to_dict(), 200)
    else:
        # Log and return 404
        message = "Received content query request for unknown list type: '{0}'".format(list_type)
        logger.error(request, message)
        return json(request, message, 404)


@search_blueprint.route('/<list_type>/counts', methods=['GET', 'POST'], strict_slashes=True)
async def ons_counts_query(request: ONSRequest, list_type: str) -> HTTPResponse:
    """
    Handles type counts queries to the <list_type> API.
    :param request:
    :param list_type: The list_type to query against (i.e ons, onsdata or onspublications; see api.search.list_type.py)
    :return:
    """
    # Parse list_type to enum
    if ListType.is_list_type(list_type):
        list_type_enum: ListType = ListType.from_str(list_type)
        # Initialise the search engine
        sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.ONS)

        # Perform the request
        search_result: SearchResult = await sanic_search_engine.type_counts_query(request, list_type_enum)

        return json(request, search_result.to_dict(), 200)
    else:
        # Log and return 404
        message = "Received type counts request for unknown list type: '{0}'".format(list_type)
        logger.error(request, message)
        return json(request, message, 404)


@search_blueprint.route('/ons/featured', methods=['GET', 'POST'], strict_slashes=True)
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
