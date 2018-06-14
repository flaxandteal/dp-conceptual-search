from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.exceptions import InvalidUsage

from server.users import get_user_id
from server.recommend.engine import RecommendationEngine

from typing import Callable

recommend_blueprint = Blueprint('recommend', url_prefix='recommend')


async def update(request: Request, term: str, update_func: Callable) -> HTTPResponse:
    """
    Performs a generic reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :param update_func:
    :return:
    """
    from server.users.user import User

    user_id = get_user_id(request)

    if user_id is not None:
        engine = RecommendationEngine(user_id)
        return await engine.update_user(request, term, update_func)
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


@recommend_blueprint.route('/update/positive/<term>', methods=['POST'])
async def positive_update(request: Request, term: str):
    """
    Performs a positive reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :return:
    """
    from server.users.distance_utils import default_move_session_vector

    return await update(request, term, default_move_session_vector)


@recommend_blueprint.route('/update/negative/<term>', methods=['POST'])
async def negative_update(request: Request, term: str):
    """
    Performs a negative reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :return:
    """
    from server.users.distance_utils import negative_move_session_vector

    return await update(request, term, negative_move_session_vector)
