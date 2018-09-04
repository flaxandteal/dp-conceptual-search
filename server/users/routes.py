from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from sanic_openapi import doc

from server.users import get_user, get_user_id
from core.users.user import User

user_blueprint = Blueprint('users', url_prefix='/users')


@doc.summary("Creare a user, using the _ga cookie to set the users ID")
@user_blueprint.route('/create', methods=['PUT'], strict_slashes=True)
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


@doc.summary("Find a user by their ID (uses _ga cookie)")
@user_blueprint.route('/find', methods=['GET'], strict_slashes=True)
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


@doc.summary("Find a user by their ID")
@user_blueprint.route('/find/<user_id>', methods=['GET'], strict_slashes=True)
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


@doc.summary("Delete a user by their ID")
@user_blueprint.route('/delete/<user_id>', methods=['DELETE'], strict_slashes=True)
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
