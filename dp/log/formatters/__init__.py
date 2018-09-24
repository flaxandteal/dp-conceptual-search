"""
Defines custom JSON formatters for logging
"""
from datetime import datetime
from pythonjsonlogger import jsonlogger

level_style_dict = {
    'INFO': 'rainbow_dash',
    'DEBUG': 'default',
    'WARN': 'monokai',
    'ERROR': 'vim'
}


class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def __init__(self, *args, coloured_logging: bool=True, **kwargs):
        super(CustomJsonFormatter, self).__init__(*args, **kwargs)

        self.coloured_logging = coloured_logging

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

    def format(self, record):
        formatted_json = super(CustomJsonFormatter, self).format(record)

        if self.coloured_logging:
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

