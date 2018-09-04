from sanic import Blueprint
from sanic.request import Request

from sanic_openapi import doc

from ons.search.search_engine import SearchEngine

from server.search import search_with_client
from server.search.list_type import ListType

search_blueprint = Blueprint('search', url_prefix='/search')


@doc.summary("Proxies an Elasticsearch query as JSON over HTTP")
@search_blueprint.route('/', methods=['POST'], strict_slashes=True)
async def proxy_elatiscsearch_query(request: Request):
    """
    Proxies Elasticsearch queries to support legacy babbage APIs going forwards.
    :param request:
    :return:
    """
    from json import loads

    from sanic.response import json as json_response
    from sanic.exceptions import InvalidUsage

    from ons.search.indicies import Index
    from ons.search.response import ONSResponse
    from ons.search.search_engine import SearchEngine

    from server.requests import extract_page, extract_page_size

    body = request.json

    if body is not None and isinstance(body, dict) and "query" in body:

        query = loads(body.get("query"))
        type_filters = body.get("filter")

        current_app = request.app
        es_client = current_app.es_client

        s = SearchEngine(using=es_client, index=Index.ONS.value)
        s.update_from_dict(query)

        if len(type_filters) > 0:
            s: SearchEngine = s.type_filter(type_filters)

        response: ONSResponse = await s.execute()

        # Get page_number/size params
        page_number: int = extract_page(request)
        page_size: int = extract_page_size(request)

        hits = response.response_to_json(page_number, page_size)
        aggs = response.aggs_to_json()

        result = {**hits, **aggs}

        return json_response(result, 200)
    raise InvalidUsage("Request body not specified")


@doc.summary("Default ONS search API for population the Search Engine Results Page (SERP)")
@doc.consumes({"q": str})
@search_blueprint.route('/ons/<endpoint>', methods=['GET', 'POST'], strict_slashes=True)
async def search_ons(request: Request, endpoint: str):
    return await search_with_client(request, ListType.ONS, endpoint, SearchEngine)


@doc.summary("Default ONS search API for population the SERP, using the data filter")
@doc.consumes({"q": str})
@search_blueprint.route('/onsdata/<endpoint>', methods=['GET', 'POST'], strict_slashes=True)
async def search_ons_data(request: Request, endpoint: str):
    return await search_with_client(request, ListType.ONS_DATA, endpoint, SearchEngine)


@doc.summary("Default ONS search API for population the SERP, using the publications filter")
@doc.consumes({"q": str})
@search_blueprint.route('/onspublications/<endpoint>', methods=['GET', 'POST'], strict_slashes=True)
async def search_ons_publications(request: Request, endpoint: str):
    return await search_with_client(request, ListType.ONS_PUBLICATIONS, endpoint, SearchEngine)


@doc.summary("Route for finding pages by their URI")
@search_blueprint.route('/uri/', strict_slashes=True)
@search_blueprint.route('/uri/<path:path>', strict_slashes=True)
async def find_document(request: Request, path: str=''):
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
        result = response.response_to_json(1, 1)

        return result
    raise NotFound("No document found with uri '%s'" % path)
