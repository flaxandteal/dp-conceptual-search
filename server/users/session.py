import numpy as np
from bson import ObjectId
from typing import Callable

from sanic.request import Request

from server.app import BaseModel
from server.mongo.document import Document
from server.users.distance_utils import default_move_session_vector

from server.word_embedding.supervised_models import load_model, SupervisedModels


model = load_model(SupervisedModels.ONS)
dim = model.get_dimension()


class Session(BaseModel, Document):
    __coll__ = 'user_sessions'
    __unique_fields__ = ['user_id', 'session_id']

    session_id_key = '_gid'

    def __init__(
            self,
            user_id: ObjectId,
            session_id: str,
            session_vector: list=None,
            **kwargs):
        super(Session, self).__init__(**kwargs)
        self.user_id = user_id
        self.session_id = session_id
        if session_vector is None:
            session_vector = np.zeros(dim).tolist()
        self.session_vector = session_vector

    @classmethod
    def create_session(cls, request: Request, user_id: ObjectId):
        session_id: str = request.cookies.get(Session.session_id_key)
        return Session(user_id, session_id)

    def to_dict(self):
        return dict(user_id=self.user_id,
                    session_id=self.session_id,
                    session_vector=self.session_vector
                    )

    def to_json(self):
        return dict(_id=str(self.id),
                    user_id=str(self.user_id),
                    session_id=self.session_id,
                    session_vector=self.session_vector
                    )

    async def update(self):
        doc = dict(session_vector=self.session_vector)
        return await Session.update_one({'_id': self.id}, {'$set': doc})

    @classmethod
    async def find_by_session_id(cls, session_id):
        return await Session.find_one(filter=dict(session_id=session_id))

    @property
    def session_array(self) -> np.ndarray:
        return np.array(self.session_vector)

    async def update_session_vector(
            self,
            search_term: str,
            update_func: Callable=default_move_session_vector,
            **kwargs):
        """
        Update this sessions term vector
        :param search_term:
        :param update_func: Callable - function which takes the original session vector, term vector
        and (optional) kwargs and updates the session vector to reflect user interest.
        :return:
        """
        session_vec = self.session_array
        term_vector = model.get_sentence_vector(search_term.lower())

        # Update the user vector
        if np.all(session_vec == 0.):
            self.session_vector = term_vector.tolist()
        else:
            # Move the user vector towards the term vector
            new_session_vec = update_func(session_vec, term_vector, **kwargs)
            self.session_vector = new_session_vec.tolist()

        # Write the changes
        await self.update()
