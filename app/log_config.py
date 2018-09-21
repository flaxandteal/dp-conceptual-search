import os

from pythonjsonlogger import jsonlogger
from datetime import datetime

from config.config_core import COLOURED_LOGGING_ENABLED, PRETTY_LOGGING

log_level = os.environ.get("SEARCH_LOG_LEVEL", "INFO")

level_style_dict = {
    'INFO': 'rainbow_dash',
    'DEBUG': 'default',
    'WARN': 'monokai',
    'ERROR': 'vim'
}


class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def __init__(self, *args, **kwargs):
        super(CustomJsonFormatter, self).__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(
            CustomJsonFormatter,
            self).add_fields(
            log_record,
            record,
            message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        log_record['namespace'] = 'dp-conceptual-search'

        if log_record.get('status') and not isinstance(
                log_record['status'], str):
            # Convert to str to stay consistent with other apps
            log_record['status'] = str(log_record['status'])

    def format(self, record):
        formatted_json = super(CustomJsonFormatter, self).format(record)

        if COLOURED_LOGGING_ENABLED:
            from logging import LogRecord
            from pygments import highlight, lexers, formatters
            if isinstance(record, LogRecord):
                colorful_json = highlight(
                    formatted_json,
                    lexers.JsonLexer(),
                    formatters.Terminal256Formatter(
                        style=level_style_dict.get(
                            record.levelname,
                            'default')))
            else:
                colorful_json = highlight(
                    formatted_json,
                    lexers.JsonLexer(),
                    formatters.Terminal256Formatter())
            return colorful_json
        else:
            return formatted_json


class PrettyCustomJsonFormatter(CustomJsonFormatter):
    def __init__(self, *args, **kwargs):
        super(PrettyCustomJsonFormatter, self).__init__(
            *args, json_indent=4, **kwargs)


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
    'pathname'
]

custom_format = ' '.join(log_format(supported_keys))

default_log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': custom_format,
            'class': 'app.log_config.PrettyCustomJsonFormatter' if PRETTY_LOGGING else 'app.log_config.CustomJsonFormatter'
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
