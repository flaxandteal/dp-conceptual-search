from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import InvalidUsage

user_blueprint = Blueprint('users', url_prefix='/users')


async def get_user(user_id: str):
    """
    Loads a user by first trying the supplied user_id, then hashing if not found and trying again.
    :param user_id:
    :return:
    """
    from server.anonymize import hash_value
    from server.users.user import User

    user = await User.find_one(filter=dict(user_id=user_id))
    if user is None:
        user = await User.find_one(filter=dict(user_id=hash_value(user_id)))
    return user


@user_blueprint.route('/create', methods=['PUT'])
async def create(request: Request):
    from server.users.user import User

    uid = request.cookies.get(User.user_id_key)
    if uid is not None:
        user = User(uid)

        await user.write()
        return json(user.to_json(), 200)
    raise InvalidUsage(
        "Must supply '%s' cookie to create user" %
        User.user_id_key)


@user_blueprint.route('/find/<user_id>', methods=['GET'])
async def find(request: Request, user_id: str):
    user = await get_user(user_id)

    if user is not None:
        doc = user.to_json()
        doc['user_vector'] = await user.get_user_vector()
        return json(doc, 200)
    return json("User '%s' not found" % user_id, 404)


@user_blueprint.route('/delete/<user_id>', methods=['DELETE'])
async def delete(request: Request, user_id: str):
    user = await get_user(user_id)

    if user is not None:
        await user.destroy()
        return json("User '%s' deleted" % user_id, 200)
    return json("User '%s' not found" % user_id, 404)


@user_blueprint.route('/update/<term>', methods=['POST'])
async def update(request: Request, term: str):
    """
    Update a user via their latest session using the provided term
    :param request:
    :param user_id:
    :param term:
    :return:
    """
    from server.users.user import User

    uid = request.cookies.get(User.user_id_key)
    if uid is not None:
        user = await get_user(uid)

        if user is not None:
            from server.users.session import Session
            session: Session = await user.get_latest_session()

            if session is None:
                if Session.session_id_key in request.cookies:
                    # Create the session
                    session: Session = Session.create_session(request, user.id)

                    # Save the session
                    await session.write()
                else:
                    return json(
                        "Unable to create session for user '%s'" %
                        uid, 404)
            # Session should always exist here
            await session.update_session_vector(term)

            doc = user.to_json()
            user_vector = await user.get_user_vector()
            doc['user_vector'] = user_vector.tolist()

            return json(doc, 200)
        else:
            return json("User '%s' not found" % uid, 404)
    raise InvalidUsage(
        "Must supply '%s' cookie to create user" %
        User.user_id_key)


@user_blueprint.route('/similarity/<user_id>/<term>', methods=['GET'])
async def similarity(request: Request, user_id: str, term: str):
    """
    Measure how likely this user is to be interested in the specified term
    :param request:
    :param user_id:
    :param term:
    :return:
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
