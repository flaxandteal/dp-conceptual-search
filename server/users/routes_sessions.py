from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from sanic_openapi import doc

sessions_blueprint = Blueprint('sessions', url_prefix='/sessions')


@doc.summary("Create a user sessions for the desired user")
@sessions_blueprint.route('/create/<user_id>', methods=['PUT'], strict_slashes=True)
async def create(request: Request, user_id: str):
    from core.users.user import User
    from core.users.session import Session

    session_id = request.cookies.get(Session.session_id_key)

    if session_id is not None:
        user = await User.find_one(filter=dict(user_id=user_id))
        if user is not None:
            session = Session(user.id, session_id)

            await session.write()

            return json(session.to_json(), 200)

        return json("User '%s' not found" % user_id, 404)
    raise InvalidUsage(
        "Must supply '%s' cookie to create user session" %
        Session.session_id_key)
