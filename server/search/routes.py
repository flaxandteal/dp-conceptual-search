from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.search import execute_search
from server.requests import get_form_param
from server.search.search_engine import SearchEngine

search_blueprint = Blueprint('search', url_prefix='/search')


@search_blueprint.route('/ons', methods=["GET", "POST"])
async def search(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine
    :param request:
    :return:
    """
    from server.search.type_filter import all_filter_funcs

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, all_filter_funcs())

        response = await execute_search(request, SearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/data', methods=["GET", "POST"])
async def search_data(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine. Limits type filters for SearchData endpoint.
    :param request:
    :return:
    """
    from server.search.type_filter import filters

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, filters["data"])

        response = await execute_search(request, SearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/publications', methods=["GET", "POST"])
async def search_publications(request: Request):
    """
    Performs a search request using the standard ONS SearchEngine. Limits type filters for SearchPublications endpoint.
    :param request:
    :return:
    """
    from server.search.type_filter import filters

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, filters["publications"])

        response = await execute_search(request, SearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")


@search_blueprint.route('/ons/departments', methods=["GET", "POST"])
async def search_departments(request: Request):
    """
    Performs the ONS departments query
    :param request:
    :return:
    """
    from server.search.indices import Index

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
            "results": [hit for hit in response.hits.hits]
        }

        return json(result)
    raise InvalidUsage("no query provided")
