from sanic import Blueprint
from sanic.request import Request
from sanic.exceptions import InvalidUsage, NotFound

from core.users.user import User

from typing import Callable

conceptual_search_blueprint = Blueprint(
    'conceptual_search',
    url_prefix='/search/conceptual')


available_list_types = ['ons', 'onsdata', 'onspublications']


async def get_user_vector(request: Request):
    """
    Extract user vector using user id cookie
    :param request:
    :return:
    """
    user_vector = None
    if User.user_id_key in request.cookies:
        user_id = request.cookies.get(User.user_id_key)
        user: User = await User.find_by_user_id(user_id)

        if user is not None:
            # Compute the user vector
            user_vector = await user.get_user_vector()

    return user_vector


async def search(request: Request, fn: Callable, list_type: str, **kwargs):
    from ons.search.conceptual.search_engine import ConceptualSearchEngine
    if list_type in available_list_types:
        user_vector = await get_user_vector(request)
        return await fn(request, ConceptualSearchEngine, list_type=list_type, user_vector=user_vector, **kwargs)
    raise NotFound("No route for list type '%s'" % list_type)


@conceptual_search_blueprint.route(
    '/<list_type>/content', methods=['GET', 'POST'])
async def ons_content_query(request: Request, list_type: str):
    """
    ONS content query
    :param request:
    :param list_type: ons, onsdata or onspublications
    :return:
    """
    from server.search.utils import content_query

    return await search(request, content_query, list_type)


@conceptual_search_blueprint.route(
    '/<list_type>/counts', methods=['GET', 'POST'])
async def type_counts_query(request: Request, list_type: str):
    """
    ONS type counts query
    :param request:
    :param list_type: ons, onsdata or onspublications
    :return:
    """
    from server.search.utils import type_counts_query

    return await search(request, type_counts_query, list_type)


@conceptual_search_blueprint.route(
    '/<list_type>/featured', methods=['GET', 'POST'])
async def featured_result_query(request: Request, list_type: str):
    """
    Redirects to search featured result
    :param request:
    :param list_type:
    :return:
    """
    from urllib import parse
    from sanic.response import redirect

    search_term = request.args.get("q")
    search_term_encoded = parse.quote_plus(search_term)

    return redirect(
        '/search/%s/featured?q=%s' %
        (list_type, search_term_encoded))
