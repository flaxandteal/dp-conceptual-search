from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.users import get_user, get_user_id
from server.users.user import User

user_blueprint = Blueprint('users', url_prefix='/users')


@user_blueprint.route('/create', methods=['PUT'])
async def create(request: Request):
    """
    Creates a new user and inserts it into the database.
    :param request:
    :return: JSON representation of the User.
    """
    user_id = get_user_id(request)
    if user_id is not None and User.is_unique(doc=dict(user_id=user_id)):
        user = User(user_id)

        await user.write()
        return json(user.to_json(), 200)
    raise InvalidUsage(
        "Must supply unique '%s' cookie to create user" %
        User.user_id_key)


@user_blueprint.route('/find', methods=['GET'])
async def find(request: Request):
    """
    Queries mongoDB for a user with given id (retrieved from request cookies).
    :param request:
    :return: User if exists, else 404 NOT_FOUND
    """
    user_id = get_user_id(request)
    if user_id is not None:
        return await find(request, user_id)
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


@user_blueprint.route('/find/<user_id>', methods=['GET'])
async def find(request: Request, user_id: str):
    """
    Queries mongoDB for a user with given id.
    :param request:
    :return: User if exists, else 404 NOT_FOUND
    """
    user = await get_user(user_id)

    if user is not None:
        doc = user.to_json()
        doc['user_vector'] = await user.get_user_vector()
        return json(doc, 200)
    return json("User '%s' not found" % user_id, 404)


@user_blueprint.route('/delete/<user_id>', methods=['DELETE'])
async def delete(request: Request, user_id: str):
    """
    Deletes the user (and all connected sessions) with the given id.
    :param request:
    :param user_id:
    :return: 200 OK if successful. 404 NOT_FOUND if user doesn't exist.
    """
    user = await get_user(user_id)

    if user is not None:
        await user.destroy()
        return json("User '%s' deleted" % user_id, 200)
    return json("User '%s' not found" % user_id, 404)


@user_blueprint.route('/similarity/<term>', methods=['GET'])
async def similarity(request: Request, term: str):
    """
    Measure how likely the current user is to be interested in the specified term.
    :param request:
    :param term:
    :return: 200 OK with similarity score if user exists. 404 NOT_FOUND if the user doesn't exist.
    """
    user_id = get_user_id(request)
    if user_id is not None:
        return await similarity(request, user_id, term)
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


@user_blueprint.route('/similarity/<user_id>/<term>', methods=['GET'])
async def similarity(request: Request, user_id: str, term: str):
    """
    Measure how likely this user is to be interested in the specified term
    :param request:
    :param user_id:
    :param term:
    :return: 200 OK with similarity score if user exists. 404 NOT_FOUND if the user doesn't exist.
    """
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
