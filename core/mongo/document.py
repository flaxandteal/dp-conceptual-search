import abc


class Document(abc.ABC):

    async def write(self):
        t = type(self)

        write_result = await t.insert_one(self.to_dict())

        # Set our oid
        self['_id'] = write_result.inserted_id

    @classmethod
    @abc.abstractmethod
    async def insert_one(cls, doc, **kwargs):
        pass

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @abc.abstractmethod
    def to_json(self) -> dict:
        pass
