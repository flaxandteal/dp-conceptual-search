from sanic import Blueprint
from sanic.request import Request
from sanic.exceptions import InvalidUsage

from server.requests import get_form_param

from server.search import execute_search

conceptual_search_blueprint = Blueprint(
    'conceptual_search',
    url_prefix='/search/conceptual')


@conceptual_search_blueprint.route('/ons', methods=["GET", "POST"])
async def conceptual_search(request: Request):
    """
    Performs a search request using the new ConceptualSearchEngine
    :param request:
    :return:
    """
    from core.users.user import User

    from ons.search.type_filter import all_filter_funcs
    from ons.search.conceptual.search_engine import ConceptualSearchEngine

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, all_filter_funcs())

        user_vector = None
        if User.user_id_key in request.cookies:
            user_id = request.cookies.get(User.user_id_key)
            user: User = await User.find_by_user_id(user_id)

            if user is not None:
                # Compute the user vector
                user_vector = await user.get_user_vector()

        response = await execute_search(request, ConceptualSearchEngine, search_term,
                                        type_filters, user_vector=user_vector)
        return response
    raise InvalidUsage("no query provided")
