"""
This file contains all routes for the /search/conceptual API
"""
from sanic import Blueprint
from sanic.response import HTTPResponse

from dp4py_sanic.api.response import json

from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.api.search.sanic_search_engine import SanicSearchEngine
from dp_conceptual_search.ons.conceptual.client import ConceptualSearchEngine


conceptual_search_blueprint = Blueprint('conceptual search', url_prefix='/search/conceptual')


search_engine_cls = ConceptualSearchEngine


@conceptual_search_blueprint.route('/content', methods=['GET', 'POST'], strict_slashes=True)
async def conceptual_content_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles content queries to the <list_type> API.
    :param request:
    :param list_type: The list_type to query against (i.e ons, onsdata or onspublications; see api.search.list_type.py)
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.content_query(request)

    return json(request, search_result.to_dict(), 200)


@conceptual_search_blueprint.route('/counts', methods=['GET', 'POST'], strict_slashes=True)
async def conceptual_counts_query(request: ONSRequest) -> HTTPResponse:
    """
    Handles type counts queries to the <list_type> API.
    :param request:
    :param list_type: The list_type to query against (i.e ons, onsdata or onspublications; see api.search.list_type.py)
    :return:
    """
    # Initialise the search engine
    sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

    # Perform the request
    search_result: SearchResult = await sanic_search_engine.type_counts_query(request)

    return json(request, search_result.to_dict(), 200)
