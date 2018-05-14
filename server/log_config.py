import os

log_level = os.getenv("SEARCH_LOG_LEVEL", "INFO")


def log_format(x):
    return ['%({0:s})'.format(i) for i in x]


supported_keys = [
    'timestamp',
    'level',
    'pathname',
    'funcName',
    'lineno',
    'module',
    'message',
    'name',
    'process',
    'processName',
    'thread',
    'threadName'
]

custom_format = ' '.join(log_format(supported_keys))

default_log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': custom_format,
            'class': 'server.app.CustomJsonFormatter'
        },
    },
    'handlers': {
        'default': {
            'level': log_level,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': log_level,
            'propagate': True
        }
    }
}
