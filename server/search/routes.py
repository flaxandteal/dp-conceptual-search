from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.exceptions import InvalidUsage, NotFound

from ons.search.search_engine import SearchEngine

from typing import Callable

search_blueprint = Blueprint('search', url_prefix='/search')


available_list_types = ['ons', 'onsdata', 'onspublications']


@search_blueprint.route('/', methods=['POST'])
async def proxy_elatiscsearch_query(request: Request):
    """
    Proxies Elasticsearch queries to support legacy babbage APIs going forwards.
    :param request:
    :return:
    """
    from json import loads

    from sanic.response import json as json_response

    from ons.search.indicies import Index
    from ons.search.response import ONSResponse
    from ons.search.search_engine import SearchEngine

    body = request.json

    if body is not None:

        query = loads(body.get("query"))
        filters = loads(body.get("filter"))

        type_filters = []
        for f in filters:
            if isinstance(f, dict) and "value" in f:
                type_filters.append(f.get("value"))

        current_app = request.app
        es_client = current_app.es_client

        s = SearchEngine(using=es_client, index=Index.ONS.value)
        s.update_from_dict(query)

        if len(type_filters) > 0:
            s: SearchEngine = s.type_filter(type_filters)

        response: ONSResponse = await s.execute()
        hits = response.hits_to_json()
        aggs = response.aggs_to_json()

        result = {**hits, **aggs}

        return json_response(result, 200)
    raise InvalidUsage("Request body not specified")


async def search(request: Request, fn: Callable, list_type: str, **kwargs):
    from sanic.response import json

    from ons.search.search_engine import SearchEngine

    if list_type in available_list_types:
        result = await fn(request, SearchEngine, list_type=list_type, **kwargs)
        return json(result, 200)
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
    from sanic.response import json
    from ons.search.search_engine import SearchEngine
    from server.search.utils import featured_result_query

    result = await featured_result_query(request, SearchEngine)
    return json(result, 200)


@search_blueprint.route('/ons/departments', methods=["GET", "POST"])
async def departments(request: Request) -> HTTPResponse:
    """
    Performs the ONS departments query
    :param request:
    :return:
    """
    from sanic.response import json

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

        result = response.response_to_json(page_number, page_size, sort_by)

        return json(result, 200)
    raise InvalidUsage("no query provided")


@search_blueprint.route('/uri/')
@search_blueprint.route('/uri/<path:path>')
async def find_document(request: Request, path: str='') -> HTTPResponse:
    from sanic.response import json

    response = await find_document_by_uri(request, path)
    return json(response, 200)


async def find_document_by_uri(request: Request, path: str='') -> dict:
    """
    Locates a document by its uri.
    :param request:
    :param path:
    :return:
    """
    from ons.search.indicies import Index
    from ons.search.response import ONSResponse
    from ons.search.search_engine import SearchEngine

    from sanic.exceptions import NotFound

    from inspect import isawaitable

    client = request.app.es_client

    s = SearchEngine(using=client, index=Index.ONS.value)
    response: ONSResponse = s.search_by_uri(path).execute()

    if isawaitable(response):
        response = await response

    if response.hits.total > 0:
        result = response.hits_to_json()

        return result
    raise NotFound("No document found with uri '%s'" % path)
