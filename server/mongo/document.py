import abc


class Document(abc.ABC):

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @abc.abstractmethod
    def to_json(self) -> dict:
        pass

    @abc.abstractmethod
    async def write(self):
        pass
