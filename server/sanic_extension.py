import abc
from sanic import Sanic


class SanicExtension(abc.ABC):
    def __init__(self, app: Sanic=None):
        self.app = app

        if app:
            self.init_app(app=app)

    @abc.abstractmethod
    def init_app(self, app: Sanic, **kwargs) -> None:
        pass
