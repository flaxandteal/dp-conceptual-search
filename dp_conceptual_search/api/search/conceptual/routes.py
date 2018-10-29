"""
This file contains all routes for the /search/conceptual API
"""
from sanic import Blueprint
from sanic.response import HTTPResponse

from dp_conceptual_search.api.log import logger
from dp_conceptual_search.api.response import json
from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.api.search.list_type import ListType
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.api.search.sanic_search_engine import SanicSearchEngine
from dp_conceptual_search.ons.search.conceptual.client.conceptual_search_engine import ConceptualSearchEngine


conceptual_search_blueprint = Blueprint('conceptual search', url_prefix='/search/conceptual')


search_engine_cls = ConceptualSearchEngine


@conceptual_search_blueprint.route('/<list_type>/content', methods=['GET', 'POST'], strict_slashes=True)
async def conceptual_content_query(request: ONSRequest, list_type: str) -> HTTPResponse:
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
        sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

        # Perform the request
        search_result: SearchResult = await sanic_search_engine.content_query(request, list_type_enum)

        return json(request, search_result.to_dict(), 200)
    else:
        # Log and return 404
        message = "Received content query request for unknown list type: '{0}'".format(list_type)
        logger.error(request.request_id, message)
        return json(request, message, 404)


@conceptual_search_blueprint.route('/<list_type>/counts', methods=['GET', 'POST'], strict_slashes=True)
async def conceptual_counts_query(request: ONSRequest, list_type: str) -> HTTPResponse:
    """
    Handles type counts queries to the <list_type> API.
    :param request:
    :param list_type: The list_type to query against (i.e ons, onsdata or onspublications; see api.search.list_type.py)
    :return:
    """
    # Parse list_type to enum
    if ListType.is_list_type(list_type):
        # Initialise the search engine
        sanic_search_engine = SanicSearchEngine(request.app, search_engine_cls, Index.ONS)

        # Perform the request
        search_result: SearchResult = await sanic_search_engine.type_counts_query(request)

        return json(request, search_result.to_dict(), 200)
    else:
        # Log and return 404
        message = "Received type counts request for unknown list type: '{0}'".format(list_type)
        logger.error(request.request_id, message)
        return json(request, message, 404)
