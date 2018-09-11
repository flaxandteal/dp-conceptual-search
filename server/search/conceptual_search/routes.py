from sanic import Blueprint
from sanic.request import Request

from server.search.list_type import ListType

conceptual_search_blueprint = Blueprint(
    'conceptual_search',
    url_prefix='/search/conceptual')


@conceptual_search_blueprint.route('/ons/<endpoint>', methods=['GET', 'POST'], strict_slashes=True)
async def search_ons(request: Request, endpoint: str):
    return await search(request, ListType.ONS, endpoint)


@conceptual_search_blueprint.route('/onsdata/<endpoint>', methods=['GET', 'POST'], strict_slashes=True)
async def search_ons_data(request: Request, endpoint: str):
    return await search(request, ListType.ONS_DATA, endpoint)


@conceptual_search_blueprint.route('/onspublications/<endpoint>', methods=['GET', 'POST'], strict_slashes=True)
async def search_ons_publications(request: Request, endpoint: str):
    return await search(request, ListType.ONS_PUBLICATIONS, endpoint)


async def search(request: Request, list_type: ListType, endpoint: str):
    """
    Single route for all ONS list types and possible endpoints. Responsible for populating the SERP.
    :param request:
    :param list_type:
    :param endpoint:
    :return:
    """
    from ons.search.conceptual.search_engine import ConceptualSearchEngine

    from server.search import search_with_client
    from server.search.endpoint import Endpoint
    from server.search.conceptual_search.utils import get_user_vector

    if endpoint == Endpoint.FEATURED.value:
        # Redirect to standard featured result API
        from urllib import parse
        from sanic.response import redirect

        search_term = request.args.get("q")
        search_term_encoded = parse.quote_plus(search_term)

        return redirect(
            '/search/%s/featured?q=%s' %
            (list_type.value, search_term_encoded))

    user_vector = await get_user_vector(request)

    return await search_with_client(request, list_type, endpoint, ConceptualSearchEngine, user_vector=user_vector)
