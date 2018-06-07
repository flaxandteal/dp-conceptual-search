from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

user_blueprint = Blueprint('users', url_prefix='/users')


@user_blueprint.route('/create', methods=['PUT'])
async def create(request: Request):
    from uuid import uuid1
    from server.users.user import User

    uid = str(uuid1())
    user = User(uid)

    await user.write()
    return json(user.to_dict(), 200)


@user_blueprint.route('/find/<user_id>', methods=['GET'])
async def find(request: Request, user_id: str):
    from server.users.user import User

    user = await User.find_one(filter=dict(user_id=user_id))
    return json(user.to_dict(), 200)
