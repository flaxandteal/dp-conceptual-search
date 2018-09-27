"""
Defines custom Sanic error handlers
"""
import sanic
import sanic.exceptions
from sanic.response import json

from api.log import logger
from api.request import ONSRequest


class ErrorHandlers(object):

    @staticmethod
    def register(app: sanic.Sanic):
        # Explicitly handle RequestTimeouts -> These are logged out as Errors by default (unwanted)
        @app.exception(sanic.exceptions.RequestTimeout)
        def timeout(request: ONSRequest, exception: sanic.exceptions.SanicException):
            logger.debug(request, "RequestTimeout from error_handler.", exc_info=exception)
            return json({"message": "RequestTimeout from error_handler."}, exception.status_code)
