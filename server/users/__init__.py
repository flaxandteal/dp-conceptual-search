from sanic.request import Request
from server.users.user import User


def get_user_id(request: Request) -> str:
    """
    Retrieves the user_id field from request cookies
    :param request:
    :return: user_id as str if exists, else None
    """
    return request.cookies.get(User.user_id_key, None)


async def get_user(user_id: str) -> User:
    """
    Queries mongoDB for a user with the supplied id.
    :param user_id:
    :return: User if exists, else None.
    """
    user = await User.find_one(filter=dict(user_id=user_id))
    return user
