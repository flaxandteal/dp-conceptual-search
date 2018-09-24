"""
Add namespace to all log messages
"""
from config.config_core import API_TITLE, PRETTY_LOGGING
from dp.log.formatters import CustomJsonFormatter


_json_indent = 4 if PRETTY_LOGGING else None


class SearchJsonFormatter(CustomJsonFormatter):
    def __init__(self, *args, **kwargs):
        super(SearchJsonFormatter, self).__init__(
            *args, json_indent=_json_indent, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(SearchJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['namespace'] = API_TITLE
