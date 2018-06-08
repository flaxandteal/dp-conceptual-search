from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

from server.word_embedding.supervised_models import load_model, SupervisedModels

sessions_blueprint = Blueprint('sessions', url_prefix='/sessions')

model = load_model(SupervisedModels.ONS)
dim = model.get_dimension()


@sessions_blueprint.route('/create/<user_id>', methods=['PUT'])
async def create(request: Request, user_id: str):
    from server.users.user import User
    from server.users.session import Session

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


@sessions_blueprint.route(
    '/update/<user_id>/<session_id>/<term>',
    methods=['POST'])
async def update(request: Request, user_id: str, session_id: str, term: str):
    from server.users.user import User
    from server.users.session import Session

    user = await User.find_one(filter=dict(user_id=user_id))
    if user is not None:
        session = await Session.find_one(filter=dict(user_id=user.id, session_id=session_id))

        if session is not None:
            try:
                await session.update_session_vector(term)
            except Exception as e:
                return json(
                    'Unable to update user/session: %s / %s. Exception: %s' %
                    (user_id, session_id, e), 500)

            return json(session.to_json(), 200)
        return json(
            "Session '%s' not found for user %s" %
            (session_id, user_id), 404)
    return json("User '%s' not found" % user_id, 404)
