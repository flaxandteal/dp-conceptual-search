from sanic.handlers import ErrorHandler
from sanic.exceptions import SanicException


class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        # Here, we have access to the exception object
        # and can do anything with it (log, send to external service, etc)

        # Some exceptions are trivial and built into Sanic (404s, etc)
        if not isinstance(exception, SanicException):
            if hasattr(exception, "status_code"):
                exception = SanicException(status_code=exception.status_code, message=exception.message)
            else:
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

    return app
