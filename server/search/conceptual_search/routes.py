from typing import Callable
from sanic import Sanic, Blueprint
from sanic.request import Request
from sanic.exceptions import NotFound

from core.users.user import User

from server.search.routes import available_list_types

conceptual_search_blueprint = Blueprint(
    'conceptual_search',
    url_prefix='/search/conceptual')


async def get_user_vector(request: Request):
    """
    Extract user vector using user id cookie
    :param request:
    :return:
    """
    from core.utils import service_is_available

    current_app: Sanic = request.app

    host = current_app.config.get('MONGO_DEFAULT_HOST')
    port = int(current_app.config.get('MONGO_DEFAULT_PORT'))

    if current_app.config.get("USER_RECOMMENDATION_ENABLED", False) and service_is_available(host, port):
        user_vector = None
        if User.user_id_key in request.cookies:
            user_id = request.cookies.get(User.user_id_key)
            user: User = await User.find_by_user_id(user_id)

            if user is not None:
                # Compute the user vector
                user_vector = await user.get_user_vector()

        return user_vector
    return None


async def search(request: Request, fn: Callable, list_type: str, **kwargs):
    """
    Performs search with optional user rescore if url param user_vector_query is set to true
    :param request:
    :param fn:
    :param list_type:
    :param kwargs:
    :return:
    """
    from sanic.response import json

    from ons.search.conceptual.search_engine import ConceptualSearchEngine

    user_vector_query = request.args.get('user_vector_query', 'false')
    if isinstance(user_vector_query, str):
        user_vector_query: bool = user_vector_query.lower() == 'true'

    if list_type in available_list_types:
        user_vector = await get_user_vector(request) if user_vector_query else None
        result = await fn(request, ConceptualSearchEngine, list_type=list_type, user_vector=user_vector, **kwargs)
        return json(result, 200)
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
