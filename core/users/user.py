import numpy as np

from typing import List

from core.mongo import BaseModel
from core.mongo.document import Document

from core.users.session import Session


class User(BaseModel, Document):
    __coll__ = 'users'
    __unique_fields__ = ['user_id']

    user_id_key = '_ga'

    def __init__(self, user_id: str, **kwargs):
        super(User, self).__init__(**kwargs)
        self.user_id = user_id

    def to_dict(self):
        return dict(
            user_id=self.user_id)

    def to_json(self):
        return dict(_id=str(self.id),
                    user_id=str(self.user_id)
                    )

    async def destroy(self, **kwargs):
        """
        Deletes this user AND all attached sessions
        :param kwargs:
        :return:
        """
        sessions: List[Session] = await self.get_all_sessions()

        for session in sessions:
            await session.destroy()

        return await self.__class__.delete_one({'_id': self.id}, **kwargs)

    async def get_latest_session(self) -> Session:
        """
        Returns the most recent user session
        :return:
        """
        cursor = await Session.find(filter=dict(user_oid=self.id), sort='_id desc', limit=1)

        if len(cursor.objects) > 0:
            return cursor.objects[0]
        return None

    async def get_all_sessions(self) -> List[Session]:
        """
        Returns all sessions attached to this user.
        :return:
        """
        cursor = await Session.find(filter=dict(user_oid=self.id))
        sessions: List[Session] = cursor.objects

        return sessions

    async def get_user_vector(self) -> np.ndarray:
        """
        Get recent sessions and compute the User vector
        :return:
        """
        # Load sessions for current user, in descending order based on
        # generation time (ObjectId)
        sessions: List[Session] = await self.get_all_sessions()

        if len(sessions) > 0:
            # Compute vector weights which decay exponentially over time
            count = len(sessions)
            # Last weight is normalised to 1.0
            weights = np.array([np.exp(c)
                                for c in range(count)]) / np.exp(count - 1)

            # Reverse the weights to match session ordering
            weights = weights[::-1]

            # Combine vectors and weights
            vectors = np.array(
                [s.session_array * w for s, w in zip(sessions, weights)])

            # Average
            user_vec = np.mean(vectors, axis=0)

            return user_vec
        return None

    @classmethod
    async def find_by_user_id(cls, user_id):
        return await User.find_one(filter=dict(user_id=user_id))
