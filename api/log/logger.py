"""
Custom logger class for API routes which wraps the Sanic logger and injects additonal request info
"""
from sanic.log import logger


def _log(level: str, context: str, msg: str, *args, **kwargs):
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
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        elif not isinstance(kwargs['extra'], dict):
            logger.error("Incorrect usage of logger: argument 'extra' must be instanceof dict")

        kwargs['extra'] = {
            "context": context,
            **kwargs['extra']
        }
        fn(msg, *args, **kwargs)
    else:
        logger.error("Unknown log level: '{0}'".format(level))


def info(context: str, msg: str, *args, **kwargs):
    """
    Log at INFO level
    :param context:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('info', context, msg, *args, **kwargs)


def debug(context: str, msg: str, *args, **kwargs):
    """
    Log at DEBUG level
    :param context:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('debug', context, msg, *args, **kwargs)


def error(context: str, msg: str, *args, **kwargs):
    """
    Log at ERROR level
    :param context:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('error', context, msg, *args, **kwargs)


def warning(context: str, msg: str, *args, **kwargs):
    """
    Log at WARN level
    :param context:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    _log('warning', context, msg, *args, **kwargs)


def warn(context: str, msg: str, *args, **kwargs):
    """
    Shorthand for warning
    :param context:
    :param msg:
    :param args:
    :param kwargs:
    :return:
    """
    warning(context, msg, *args, **kwargs)
