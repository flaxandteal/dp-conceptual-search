from server.app import BaseModel
from server.mongo.document import Document

from server.word_embedding.supervised_models import load_model, SupervisedModels

from bson import ObjectId

import numpy as np


model = load_model(SupervisedModels.ONS)
dim = model.get_dimension()


def default_distance_measure(original_vector: np.ndarray, term_vector: np.ndarray):
    """
    Default method to measure distance between two vectors. Uses Euclidean distance.
    :param original_vector:
    :param term_vector:
    :return:
    """
    dist = term_vector - original_vector
    return dist


def default_move_session_vector(original_vector: np.ndarray, term_vector: np.ndarray):
    """
    Default method to modify a session vector to reflect interest in a term vector.
    :param original_vector: Word vector representing the present session.
    :param term_vector: Word vector representing the term of interest.
    :return: An updated word vector which has moved towards the term vector in the full N-dimensional
    vector space.
    """
    dist = default_distance_measure(original_vector, term_vector)

    return original_vector + dist / 4


class Session(BaseModel, Document):
    __coll__ = 'user_sessions'
    __unique_fields__ = ['user_id', 'session_id']

    def __init__(self, user_id: ObjectId, session_id: str, session_vector: list=None, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.user_id = user_id
        self.session_id = session_id
        if session_vector is None:
            session_vector = np.zeros(dim).tolist()
        self.session_vector = session_vector

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

    async def write(self):
        await Session.insert_one(self.to_dict())

    async def update(self):
        doc = dict(session_vector=self.session_vector)
        await Session.update_one({'_id': self.id}, {'$set': doc})

    @classmethod
    async def find_by_session_id(cls, session_id):
        return await Session.find_one(filter=dict(session_id=session_id))

    @property
    def session_array(self):
        return np.array(self.session_vector)

    async def update_session_vector(
            self,
            search_term: str,
            update_func=default_move_session_vector,
            **kwargs):
        """

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
