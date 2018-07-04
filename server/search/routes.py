from sanic import Blueprint
from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.exceptions import InvalidUsage, NotFound

from ons.search.search_engine import SearchEngine

from typing import Callable

search_blueprint = Blueprint('search', url_prefix='/search')


available_list_types = ['ons', 'onsdata', 'onspublications']


async def search(request: Request, fn: Callable, list_type: str, **kwargs):
    from ons.search.search_engine import SearchEngine

    if list_type in available_list_types:
        return await fn(request, SearchEngine, list_type=list_type, **kwargs)
    raise NotFound("No route for list type '%s'" % list_type)


@search_blueprint.route('/<list_type>/content', methods=['GET', 'POST'])
async def ons_content_query(request: Request, list_type: str):
    """
    ONS content query
    :param request:
    :param list_type: ons, onsdata or onspublications
    :return:
    """
    from server.search.utils import content_query

    return await search(request, content_query, list_type)


@search_blueprint.route('/<list_type>/counts', methods=['GET', 'POST'])
async def type_counts_query(request: Request, list_type: str):
    """
    ONS type counts query
    :param request:
    :param list_type: ons, onsdata or onspublications
    :return:
    """
    from server.search.utils import type_counts_query

    return await search(request, type_counts_query, list_type)


@search_blueprint.route('/ons/featured', methods=['GET', 'POST'])
async def featured_result_query(request: Request):
    """
    ONS featured result query
    :param request:
    :param list_type: ons, onsdata or onspublications
    :return:
    """
    from ons.search.search_engine import SearchEngine
    from server.search.utils import featured_result_query

    return await featured_result_query(request, SearchEngine)


@search_blueprint.route('/ons/departments', methods=["GET", "POST"])
async def departments(request: Request) -> HTTPResponse:
    """
    Performs the ONS departments query
    :param request:
    :return:
    """
    from ons.search.indicies import Index
    from ons.search.response import ONSResponse
    from ons.search.sort_fields import SortFields

    from server.requests import get_form_param

    search_term = request.args.get("q")
    if search_term is not None:
        import inspect

        current_app = request.app
        client = current_app.es_client

        # Get sort_by. Default to relevance
        sort_by_str = get_form_param(request, "sort_by", False, "relevance")
        sort_by = SortFields[sort_by_str]

        # Get page_number/size params
        page_number = int(get_form_param(request, "page", False, 1))
        page_size = int(get_form_param(request, "size", False, 10))

        s = SearchEngine(using=client, index=Index.DEPARTMENTS.value)
        response: ONSResponse = s.departments_query(
            search_term, page_number, page_size).execute()
        if inspect.isawaitable(response):
            response = await response

        result = response.hits_to_json(page_number, page_size, sort_by)

        return json(result)
    raise InvalidUsage("no query provided")


@search_blueprint.route('/uri/')
@search_blueprint.route('/uri/<path:path>')
async def find_document(request: Request, path: str='') -> HTTPResponse:
    response = await find_document_by_uri(request, path)
    return json(response)


async def find_document_by_uri(request: Request, path: str='') -> dict:
    """
    Locates a document by its uri.
    :param request:
    :param path:
    :return:
    """
    from ons.search.indicies import Index
    from ons.search.response import marshall_hits
    from ons.search.queries import match_by_uri
    from ons.search.search_engine import SearchEngine

    from sanic.exceptions import NotFound

    from inspect import isawaitable

    client = request.app.es_client

    s = SearchEngine(using=client, index=Index.ONS.value)
    s = s.query(match_by_uri(path))

    response = s.execute()
    if isawaitable(response):
        response = await response

    if response.hits.total > 0:
        result = {
            "numberOfResults": response.hits.total,
            "took": response.took,
            "results": marshall_hits(response.hits)
        }

        return result
    raise NotFound("No document found with uri '%s'" % path)
