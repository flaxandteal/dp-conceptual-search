from core.users.user import User
from core.users.session import Session
from core.users.distance_utils import default_move_session_vector

from server.word_embedding.sanic_supervised_models import load_model, SupervisedModels

from typing import Callable
import numpy as np


class RecommendationEngine(object):

    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id

        # Get a handle on the model - NB it has already been loaded into memory
        # by this point.
        self.model = load_model(SupervisedModels.ONS)
        self.dim = self.model.get_dimension()

    async def get_user(self) -> User:
        """
        Loads a user by first trying the supplied user_id, then hashing if not found and trying again.
        :return:
        """
        from server.users import get_user

        user: User = await get_user(self.user_id)

        if user is None:
            # Create the user
            user: User = User(self.user_id)
            await user.write()
        return user

    async def get_latest_session(self) -> Session:
        """
        Loads the latest session for the current user
        :return:
        """
        user = await self.get_user()
        session = await user.get_latest_session()

        if session is None:
            # Create the session

            session = Session(user.id, self.session_id)
            await session.write()

        return session

    async def update_session_vector(
            self,
            term_vector: np.ndarray,
            update_func: Callable=default_move_session_vector) -> Session:
        """
        Update this sessions vector
        :param term_vector:
        :param update_func: Callable - function which takes the original session vector, term vector
        and (optional) kwargs and updates the session vector to reflect user interest.
        :return:
        """
        session = await self.get_latest_session()
        session_vec = session.session_array

        # Update the user vector
        if np.all(session_vec == 0.):
            session.set_session_vector(term_vector)
        else:
            # Move the user vector towards the term vector
            new_session_vec = update_func(session_vec, term_vector)
            session.set_session_vector(new_session_vec)

        # Write the changes
        return await session.update()

    async def update_session_vector_by_term(
            self,
            search_term: str,
            update_func: Callable=default_move_session_vector) -> Session:
        """
        Update this sessions term vector
        :param search_term:
        :param update_func: Callable - function which takes the original session vector, term vector
        and (optional) kwargs and updates the session vector to reflect user interest.
        :return:
        """
        term_vector = self.model.get_sentence_vector(search_term.lower())
        return await self.update_session_vector(term_vector, update_func=update_func)
