from sanic import Sanic
from sanic.request import Request

from core.users.user import User


async def get_user_vector(request: Request):
    """
    Extract user vector using user id cookie
    :param request:
    :return:
    """
    from core.utils import service_is_available

    current_app: Sanic = request.app

    host = current_app.config.get('MONGO_DEFAULT_HOST')
    port = int(current_app.config.get('MONGO_DEFAULT_PORT'))

    if current_app.config.get("USER_RECOMMENDATION_ENABLED", False) and service_is_available(host, port):
        user_vector = None
        if User.user_id_key in request.cookies:
            user_id = request.cookies.get(User.user_id_key)
            user: User = await User.find_by_user_id(user_id)

            if user is not None:
                # Compute the user vector
                user_vector = await user.get_user_vector()

        return user_vector
    return None