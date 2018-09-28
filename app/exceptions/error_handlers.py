"""
Defines custom Sanic error handlers
"""
import sanic.exceptions
from sanic.response import json
from sanic.log import logger as sanic_logger

from app.sanic_search import SanicSearch
from api.log import logger
from api.request import ONSRequest


class ErrorHandlers(object):

    @staticmethod
    def register(app: SanicSearch):
        # Explicitly handle RequestTimeouts -> These are logged out as Errors by default (unwanted)
        @app.exception(sanic.exceptions.RequestTimeout)
        def timeout(request: ONSRequest, exception: sanic.exceptions.SanicException):
            if request is None:
                # Request has timed out and as such was awaited by the server (no longer exists)
                sanic_logger.debug("RequestTimeout from error_handler for null request.", exc_info=exception)
            else:
                # Cover any future API changes which could see the request preserved during timeout (also log out
                # request context)
                logger.debug(request, "RequestTimeout from error_handler.", exc_info=exception)
            return json({"message": "RequestTimeout from error_handler."}, exception.status_code)
