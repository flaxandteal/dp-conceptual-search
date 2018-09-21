"""
Custom logger class for API routes which wraps the Sanic logger and injects additonal request info
"""
from sanic.log import logger

from api.request.ons_request import ONSRequest


def _log(level: str, request: ONSRequest, msg: str, *args, **kwargs):
    """
    Log the given message with additional info from the request
    :param level:
    :param request:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    if hasattr(logger, level):
        fn = getattr(logger, level)
        kwargs['extra'] = {
            ONSRequest.request_id_log_key, request.request_id
        }
        fn(msg, *args, **kwargs)
    else:
        logger.error("Unknown log level: '{0}'".format(level))


def info(request: ONSRequest, msg: str, *args, **kwargs):
    """
    Log at INFO level
    :param request:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log(lo, request, msg, *args, **kwargs)


def debug(request: ONSRequest, msg: str, *args, **kwargs):
    """
    Log at DEBUG level
    :param request:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('debug', request, msg, *args, **kwargs)


def error(request: ONSRequest, msg: str, *args, **kwargs):
    """
    Log at ERROR level
    :param request:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('error', request, msg, *args, **kwargs)


def warning(request: ONSRequest, msg: str, *args, **kwargs):
    """
    Log at WARN level
    :param request:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('warning', request, msg, *args, **kwargs)


def warn(request: ONSRequest, msg: str, *args, **kwargs):
    """
    Shorthand for warning
    :param request:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    warning(request, msg, *args, **kwargs)
