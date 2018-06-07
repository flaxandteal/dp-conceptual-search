from server.app import BaseModel
from server.mongo.document import Document

import numpy as np


class User(BaseModel, Document):
    __coll__ = 'users'
    __unique_fields__ = ['user_id']

    def __init__(self, user_id: str, **kwargs):
        super(User, self).__init__(user_id=user_id, **kwargs)
        self.user_vector = np.zeros(150)

    def to_dict(self):
        return dict(
            _id=str(self.id),
            user_id=self['user_id'],
            user_vector=self.user_vector.tolist())

    async def write(self):
        await User.insert_one(self.to_dict())
