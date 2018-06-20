import numpy as np
from bson import ObjectId

from sanic.request import Request

from server.app import BaseModel
from server.mongo.document import Document

from server.word_embedding.supervised_models import load_model, SupervisedModels


class Session(BaseModel, Document):
    __coll__ = 'user_sessions'
    __unique_fields__ = ['user_oid', 'session_id']

    session_id_key = '_gid'

    def __init__(
            self,
            user_oid: ObjectId,
            session_id: str,
            session_vector: list=None,
            **kwargs):
        super(Session, self).__init__(**kwargs)

        self.user_oid = user_oid
        self.session_id = session_id

        self.dim = load_model(SupervisedModels.ONS).get_dimension()

        if session_vector is None:
            session_vector = np.zeros(self.dim).tolist()
        self.session_vector = session_vector

    @classmethod
    def create_session(cls, request: Request, user_id: ObjectId):
        session_id: str = request.cookies.get(Session.session_id_key)
        return Session(user_id, session_id)

    def to_dict(self):
        return dict(user_oid=self.user_oid,
                    session_id=self.session_id,
                    session_vector=self.session_vector
                    )

    def to_json(self):
        return dict(_id=str(self.id),
                    user_oid=str(self.user_oid),
                    session_id=self.session_id,
                    session_vector=self.session_vector
                    )

    async def update(self):
        doc = dict(session_vector=self.session_vector)
        await Session.update_one({'_id': self.id}, {'$set': doc})
        return self

    @classmethod
    async def find_by_session_id(cls, session_id):
        return await Session.find_one(filter=dict(session_id=session_id))

    @property
    def session_array(self) -> np.ndarray:
        return np.array(self.session_vector)

    def set_session_vector(self, session_vector: np.ndarray):
        """
        Manually sets the session vector
        :param session_vector:
        :return:
        """
        self.session_vector = session_vector.tolist()
