from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.exceptions import InvalidUsage

from server.users.user import User

from typing import Callable


class RecommendationEngine(object):

    def __init__(self, user_id: str):
        self.user_id = user_id

    async def get_user(self) -> User:
        """
        Loads a user by first trying the supplied user_id, then hashing if not found and trying again.
        :param user_id:
        :return:
        """
        from server.users import get_user

        user: User = await get_user(self.user_id)

        if user is None:
            # Create the user
            user: User = User(self.user_id)
            await user.write()
        return user

    async def update_user(self, request: Request, term: str, update_func: Callable) -> HTTPResponse:
        """
        Update a user via their latest session using the provided term
        :param request:
        :param user_id:
        :param term:
        :param update_func:
        :return:
        """
        user: User = await self.get_user()

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
                    raise InvalidUsage(
                        "Session id (%s) not specified for user '%s'" %
                        Session.session_id_key, self.user_id)
            # Session should always exist here
            await session.update_session_vector(term, update_func=update_func)

            doc = user.to_json()
            user_vector = await user.get_user_vector()
            doc['user_vector'] = user_vector.tolist()

            return json(doc, 200)
        else:
            return json("User '%s' not found" % self.user_id, 404)
