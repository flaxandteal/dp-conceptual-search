from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from server.word_embedding.supervised_models import load_model, SupervisedModels

sessions_blueprint = Blueprint('sessions', url_prefix='/sessions')

model = load_model(SupervisedModels.ONS)
dim = model.get_dimension()


@sessions_blueprint.route('/create/<user_id>', methods=['PUT'])
async def create(request: Request, user_id: str):
    from uuid import uuid1
    from server.users.user import User
    from server.users.session import Session

    user = await User.find_one(filter=dict(user_id=user_id))
    if user is not None:
        sid = str(uuid1())
        session = Session(user.id, sid)

        await session.write()

        return json(session.to_json(), 200)

    return json("Unable to find user with id '%s'" % user_id, 404)


@sessions_blueprint.route('/update/<user_id>/<session_id>/<term>', methods=['POST'])
async def update(request: Request, user_id: str, session_id: str, term: str):
    from server.users.user import User
    from server.users.session import Session

    user = await User.find_one(filter=dict(user_id=user_id))
    if user is not None:
        session = await Session.find_one(filter=dict(user_id=user.id, session_id=session_id))

        if session is not None:
            await session.update_session_vector(term)

            return json(session.to_json(), 200)
    return json("Unable to update session", 500)
