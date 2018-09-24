import logging


def log_format(x):
    return ['%({0:s})'.format(i) for i in x]


def config_for_formatter(formatter_cls: type, supported_keys: list, level: int=logging.INFO) -> dict:
    """
    Returns a logging config for the desired formatter
    :param formatter_cls: Class to use for formatting
    :param supported_keys: Supported keys for log messages
    :param level: Log level to be used
    :return:
    """
    custom_format = ' '.join(log_format(supported_keys))
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'format': custom_format,
                'class': formatter_cls.__module__ + "." + formatter_cls.__qualname__
            }
        },
        'handlers': {
            'json': {
                'class': 'logging.StreamHandler',
                'formatter': 'json'
            }
        },
        'loggers': {
            '': {
                'handlers': ['json'],
                'level': level
            }
        }
    }

    return log_config
