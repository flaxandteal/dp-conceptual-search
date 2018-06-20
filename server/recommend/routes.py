from sanic import Blueprint
from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.exceptions import InvalidUsage

from server.users import get_user_id
from server.recommend.engine import RecommendationEngine

from typing import Callable

recommend_blueprint = Blueprint('recommend', url_prefix='recommend')


def get_recommendation_engine(request: Request) -> RecommendationEngine:
    """

    :param request:
    :return:
    """
    from server.users.user import User

    user_id = get_user_id(request)

    if user_id is not None:
        engine = RecommendationEngine(request, user_id)

        return engine
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


async def update_by_term(request: Request, term: str, update_func: Callable) -> HTTPResponse:
    """
    Performs a generic reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :param update_func:
    :return:
    """
    engine = get_recommendation_engine(request)
    session = await engine.update_session_vector_by_term(term, update_func)

    return json(session.to_json(), 200)


@recommend_blueprint.route('/update/page/', methods=['GET', 'POST'])
@recommend_blueprint.route('/update/page/<path:path>', methods=['GET', 'POST'])
async def positive_update_by_document(request: Request, path: str):
    """
    Performs a generic reinforcement of the users vector, using the given term
    :param request:
    :param path:
    :return:
    """
    from server.users.distance_utils import default_move_session_vector

    engine = get_recommendation_engine(request)
    session = await engine.update_session_vector_by_doc_uri(path, default_move_session_vector)

    return json(session.to_json(), 200)


@recommend_blueprint.route('/update/positive/<term>', methods=['POST'])
async def positive_update(request: Request, term: str):
    """
    Performs a positive reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :return:
    """
    from server.users.distance_utils import default_move_session_vector
    return await update_by_term(request, term, default_move_session_vector)


@recommend_blueprint.route('/update/negative/<term>', methods=['POST'])
async def negative_update(request: Request, term: str):
    """
    Performs a negative reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :return:
    """
    from server.users.distance_utils import negative_move_session_vector
    return await update_by_term(request, term, negative_move_session_vector)


@recommend_blueprint.route('/similarity/<term>', methods=['GET'])
async def similarity(request: Request, term: str):
    """
    Measure how likely the current user is to be interested in the specified term.
    :param request:
    :param term:
    :return: 200 OK with similarity score if user exists. 404 NOT_FOUND if the user doesn't exist.
    """
    from server.users.user import User

    user_id = get_user_id(request)
    if user_id is not None:
        return await similarity(request, user_id, term)
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


@recommend_blueprint.route('/similarity/<user_id>/<term>', methods=['GET'])
async def similarity(request: Request, user_id: str, term: str):
    """
    Measure how likely this user is to be interested in the specified term
    :param request:
    :param user_id:
    :param term:
    :return: 200 OK with similarity score if user exists. 404 NOT_FOUND if the user doesn't exist.
    """
    from server.users import get_user
    from sanic.response import json

    user = await get_user(user_id)

    if user is not None:
        from server.word_embedding.supervised_models import load_model, SupervisedModels
        from server.word_embedding.utils import cosine_sim

        model = load_model(SupervisedModels.ONS)

        term_vector = model.get_sentence_vector(term)
        user_vector = await user.get_user_vector()

        sim = cosine_sim(user_vector, term_vector)

        response = {
            'user_id': user_id,
            'term': term,
            'similarity': sim
        }

        return json(response, 200)
    return json("User '%s' not found" % user_id, 404)
