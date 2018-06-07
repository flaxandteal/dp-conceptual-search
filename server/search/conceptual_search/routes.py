from sanic import Blueprint
from sanic.request import Request
from sanic.exceptions import InvalidUsage

from server.requests import get_form_param

from server.search.routes import execute_search

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
    from server.users.user import User

    from server.search.type_filter import all_filter_funcs
    from server.search.conceptual_search.conceptual_search_engine import ConceptualSearchEngine

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, all_filter_funcs())

        user_vector = None
        if '_ga' in request.cookies:
            user_id = request.cookies.get('_ga')
            user = await User.find_by_user_id(user_id)
            if user is not None:
                # Update session - TODO - move to dedication API
                latest_session = await user.get_latest_session()
                if latest_session is not None:
                    await latest_session.update_session_vector(search_term)

                    # Compute the user vector
                    user_vector = await user.get_user_vector()

        response = await execute_search(request, ConceptualSearchEngine, search_term,
                                        type_filters, user_vector=user_vector)
        return response
    raise InvalidUsage("no query provided")
