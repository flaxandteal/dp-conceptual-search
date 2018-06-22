from sanic.request import Request

from core.users.user import User
from core.users.session import Session
from core.users.distance_utils import default_move_session_vector
from server.word_embedding.sanic_supervised_models import load_model
from core.word_embedding.models.supervised import SupervisedModels

from typing import Callable
import numpy as np


class RecommendationEngine(object):

    def __init__(self, request: Request, user_id: str):
        self.request = request
        self.user_id = user_id

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
            if Session.session_id_key not in self.request.cookies:
                from sanic.exceptions import NotFound
                raise NotFound(
                    "Unabale to find/create session for user '%s'" %
                    self.user_id)

            sid = self.request.cookies.get(Session.session_id_key)
            session = Session(user.id, sid)
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

    async def update_session_vector_by_doc_uri(self, doc_uri: str, update_func: Callable) -> Session:
        """
        Update a user via their latest session using the provided document uri
        :param doc_uri:
        :param update_func:
        :return:
        """
        from server.search.routes import find_document_by_uri
        from core.search.fields import embedding_vector
        from core.word_embedding.utils import decode_float_list

        from sanic.exceptions import NotFound

        response: dict = await find_document_by_uri(self.request, doc_uri)

        # Document exists - get the embedding_vector
        documents: list = response.get('results', [])

        if len(documents) > 0:
            document = documents[0]

            doc_vector = document.get(embedding_vector.name)
            if doc_vector is not None and isinstance(doc_vector, str):
                # Decode the vector

                decoded_doc_vector = np.array(decode_float_list(doc_vector))
                return await self.update_session_vector(decoded_doc_vector, update_func)
        raise NotFound("No document found for uri '%s'" % doc_uri)
