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
    from server.search.type_filter import all_filter_funcs
    from server.search.conceptual_search.conceptual_search_engine import ConceptualSearchEngine

    search_term = request.args.get("q")
    if search_term is not None:
        # Get any content type filters
        type_filters = get_form_param(
            request, "filter", False, all_filter_funcs())
        response = await execute_search(request, ConceptualSearchEngine, search_term, type_filters)
        return response
    raise InvalidUsage("no query provided")
