from sanic import Blueprint
from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.exceptions import InvalidUsage

from server.search import execute_search
from server.requests import get_form_param

from core.search.search_engine import SearchEngine

search_blueprint = Blueprint('search', url_prefix='/search')


@search_blueprint.route('/ons', methods=["GET", "POST"])
async def search(request: Request) -> HTTPResponse:
    """
    Performs a search request using the standard ONS SearchEngine
    :param request:
    :return:
    """
    from core.search.filter_functions import all_filter_funcs

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, all_filter_funcs())

        return await execute_search(request, SearchEngine, search_term, type_filters)
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/data', methods=["GET", "POST"])
async def search_data(request: Request) -> HTTPResponse:
    """
    Performs a search request using the standard ONS SearchEngine. Limits type filters for SearchData endpoint.
    :param request:
    :return:
    """
    from core.search.filter_functions import filters

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, filters["data"])

        return await execute_search(request, SearchEngine, search_term, type_filters)
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/publications', methods=["GET", "POST"])
async def search_publications(request: Request) -> HTTPResponse:
    """
    Performs a search request using the standard ONS SearchEngine. Limits type filters for SearchPublications endpoint.
    :param request:
    :return:
    """
    from core.search.filter_functions import filters

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, filters["publications"])

        return await execute_search(request, SearchEngine, search_term, type_filters)
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/departments', methods=["GET", "POST"])
async def search_departments(request: Request) -> HTTPResponse:
    """
    Performs the ONS departments query
    :param request:
    :return:
    """
    from core.search.indices import Index
    from core.search.response import marshall_hits

    search_term = request.args.get("q")
    if search_term is not None:
        import inspect

        current_app = request.app

        client = current_app.es_client

        s = SearchEngine(using=client, index=Index.DEPARTMENTS.value)
        response = s.departments_query(search_term).execute()

        if inspect.isawaitable(response):
            response = await response

        result = {
            "numberOfResults": response.hits.total,
            "took": response.took,
            "results": marshall_hits(response.hits)
        }

        return json(result)
    raise InvalidUsage("no query provided")


@search_blueprint.route('/')
@search_blueprint.route('/<path:path>')
async def find_document(request: Request, path: str='') -> HTTPResponse:
    response = await find_document_by_uri(request, path)
    return json(response)


async def find_document_by_uri(request: Request, path: str='') -> HTTPResponse:
    """
    Locates a document by its uri.
    :param request:
    :param path:
    :return:
    """
    from core.search.indices import Index
    from core.search.response import marshall_hits
    from core.search.queries import match_by_uri
    from core.search.search_engine import SearchEngine

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
