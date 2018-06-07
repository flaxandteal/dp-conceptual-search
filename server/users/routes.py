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
    return json(user.to_json(), 200)


@user_blueprint.route('/find/<user_id>', methods=['GET'])
async def find(request: Request, user_id: str):
    from server.users.user import User

    user = await User.find_one(filter=dict(user_id=user_id))

    if user is not None:
        doc = user.to_json()
        doc['user_vector'] = await user.get_user_vector()
        return json(doc, 200)
    return json("User '%s' not found" % user_id, 404)


@user_blueprint.route('/delete/<user_id>', methods=['DELETE'])
async def delete(request: Request, user_id: str):
    from server.users.user import User

    user = await User.find_one(filter=dict(user_id=user_id))

    if user is not None:
        await user.destroy()
        return json("User '%s' deleted" % user_id, 200)
    return json("User '%s' not found" % user_id, 404)


@user_blueprint.route('/similarity/<user_id>/<term>', methods=['GET'])
async def similarity(request: Request, user_id: str, term: str):
    """
    Measure how likely this user is to be interested in the specified term
    :param request:
    :param term:
    :return:
    """
    from server.users.user import User

    user = await User.find_one(filter=dict(user_id=user_id))

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
