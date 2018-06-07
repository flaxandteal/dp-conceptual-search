from server.app import BaseModel
from server.mongo.document import Document


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
