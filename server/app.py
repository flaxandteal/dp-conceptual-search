from sanic.request import Request
from sanic.handlers import ErrorHandler
from sanic.exceptions import SanicException


class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        # Here, we have access to the exception object
        # and can do anything with it (log, send to external service, etc)

        # Some exceptions are trivial and built into Sanic (404s, etc)
        if not isinstance(exception, SanicException):
            print(exception)

        # Then, we must finish handling the exception by returning
        # our response to the client
        # For this we can just call the super class' default handler
        return super().default(request, exception)


def create_app():
    from sanic import Sanic
    from server.search.routes import search_blueprint

    app = Sanic()
    app.blueprint(search_blueprint)

    handler = CustomHandler()
    app.error_handler = handler

    @app.middleware('request')
    async def hash_ga_ids(request):
        """
        Intercepts all requests and hashes Google Analytics IDs
        :param request:
        :return:
        """
        from .security import hash_value
        assert isinstance(request, Request)

        for key in ["_ga", "_gid"]:
            if key in request.cookies:
                value = request.cookies.pop(key)
                request.cookies[key] = hash_value(value)
        print("Cookies=%s" % request.cookies)

    return app
