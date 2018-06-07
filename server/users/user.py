import numpy as np

from server.app import BaseModel
from server.mongo.document import Document

from server.word_embedding.supervised_models import load_model, SupervisedModels


model = load_model(SupervisedModels.ONS)


class User(BaseModel, Document):
    __coll__ = 'users'
    __unique_fields__ = ['user_id']

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

    async def write(self):
        await User.insert_one(self.to_dict())

    async def get_user_vector(self):
        """
        Get recent sessions and compute the User vector
        :return:
        """
        from server.users.session import Session

        # Load sessions for current user, in descending order based on generation time (ObjectId)
        cursor = await Session.find(filter=dict(user_id=self.id), sort='_id desc')
        sessions = cursor.objects

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

            if np.all(user_vec == 0.):
                return np.zeros(model.get_dimension()).tolist()
            return user_vec
        return np.zeros(model.get_dimension()).tolist()
