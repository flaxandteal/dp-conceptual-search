"""
This file contains all routes for the /search API
"""
from sanic import Blueprint
from sanic.response import HTTPResponse

from dp4py_sanic.api.response.json_response import json

from dp_conceptual_search.config import CONFIG
from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.api.search.sanic_search_engine import SanicSearchEngine
from dp_conceptual_search.api.search.conceptual import routes as conceptual_routes

search_blueprint = Blueprint('search', url_prefix='/search')

search_engine_cls = SearchEngine


@search_blueprint.route('/departments', methods=['GET'], strict_slashes=True)
async def ons_departments_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles departments queries to the departments index
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, SearchEngine, Index.DEPARTMENTS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.departments_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/', methods=['GET', 'POST'], strict_slashes=False)
async def search(request: ONSRequest) -> HTTPResponse:
    """
    API which combines the content, counts and featured result queries into one
    :param request:
    :return:
    """
    if CONFIG.API.redirect_conceptual_search:
        return await conceptual_routes.search(request)

    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    result = await sanic_search_engine.search(request)

    return json(request, result, 200)


@search_blueprint.route('/content', methods=['GET', 'POST'], strict_slashes=True)
async def ons_content_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles content queries to the API.
    :param request:
    :return:
    """
    if CONFIG.API.redirect_conceptual_search:
        return await conceptual_routes.conceptual_content_query(request)

    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.content_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/counts', methods=['GET', 'POST'], strict_slashes=True)
async def ons_counts_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the API.
    :param request:
    :return:
    """
    if CONFIG.API.redirect_conceptual_search:
        return await conceptual_routes.conceptual_counts_query(request)

    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.type_counts_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/featured', methods=['GET'], strict_slashes=True)
async def ons_featured_result_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles featured result queries (i.e product and home page census pages)
    :param request:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.featured_result_query(request)

    return json(request, search_result.to_dict(), 200)


@search_blueprint.route('/uri/', methods=['GET', 'POST'])
@search_blueprint.route('/uri/<path:path>', methods=['GET', 'POST'])
async def search_by_uri(request: ONSRequest, path: str):
    """
    Search for a page by it's uri
    :param request:
    :param path:
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.search_by_uri(request, path)

    return json(request, search_result.to_dict(), 200)

